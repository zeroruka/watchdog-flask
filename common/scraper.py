import os
import sys
from datetime import date
from threading import Thread
from time import sleep

import requests
import telepot
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.exc import IntegrityError
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

import app
from common.models import ListingsModel, db, UserModel

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telepot.Bot(TOKEN)


class TooManyConnectionRetries(Exception):
    pass


def scraper_loop(user_id, rate=5):  # Scraper loop for multithreading
    with app.app.app_context():
        try:
            user = UserModel.query.filter_by(id=user_id).first()
            init_values(user_id)  # Initialize listings database
            while user.scraper_status:
                scraper(user_id)
                sleep(rate)
            user.scraper_status = False
            db.session.commit()
        except Exception as e:
            logger.error(e)
            user.scraper_status = False
            bot.sendMessage(user_id, "Scraper stopped due to an error")
            db.session.commit()


# Finds the price, picture, and URL of the newest listing
def get_attr(soup, index):
    """
    :param soup: BeautifulSoup object
    :param index: Index of the listing on the page, 1-indexed since the first listing a null invisible object
    :return: alot of info
    """
    title = soup.find_all('div', {'class': 's-item__info'})[index].find('div', {
        'class': 's-item__title'}).text.strip().replace('New Listing', '')
    price = soup.find_all(
        'span', {'class': 's-item__price'})[index].text.strip()
    url = soup.find_all('a', {'class': 's-item__link'}
                        )[index].get('href').split('?hash')[0]
    _id = url.split('/')[-1]
    thumbnail_image = soup.find_all(
        'div', {'class': 's-item__image-wrapper'})[index].find('img').get('src')  # Low resolution image
    source_image = thumbnail_image.replace(
        's-l225', 's-l800')  # High resolution image

    try:  # Some listings don't have a status
        status = soup.find_all('span', {'class': 'SECONDARY_INFO'})[
            index].text.strip()
        new = True
        if status == 'Pre-Owned':  # There can only be 2 statuses, 'Brand New' or 'Pre-Owned'
            new = False
    except IndexError:
        new = None

    try:
        origin_country = soup.find_all('span', {'class': 's-item__location'})[index - 1].text.strip().replace('from ',
                                                                                                              '')
    except IndexError:
        origin_country = None

    try:
        postage_fee = soup.find_all('span', {'class': 's-item__shipping s-item__logisticsCost'})[
            index - 1].text.strip().replace('+', '').replace(' postage', '')  # +S$ 7.15 postage => S$ 7.15
    except IndexError:
        postage_fee = None

    try:
        seller_info = soup.find_all(
            'span', {'class': 's-item__seller-info-text'})[index - 1].text.strip()
    except IndexError:
        seller_info = None

    data = {
        'title': title,
        'price': price,
        'url': url,
        'id': _id,
        'thumbnail_image': thumbnail_image,
        'source_image': source_image,
        'new': new,
        'origin_country': origin_country,
        'postage_fee': postage_fee,
        'seller_info': seller_info
    }
    return data


# Send message to Telegram
def send_message(_urls, price, picture, url, title, chat_id, origin_country, postage_fee) -> None:
    message = f"New listing for {_urls}: {title}\n\n" \
              f"Price: {price}\n" \
              f"Origin country: {origin_country}\n" \
              f"Postage fee: {postage_fee}\n"
    bot.sendPhoto(chat_id, picture, message, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Send me there", url=url)]]))


# Get soup from eBay URL
def get_soup(url, item_name, MAX_RETRIES=5) -> BeautifulSoup:
    for retries in range(MAX_RETRIES):
        try:
            # Get response
            response = requests.get(url)
            # Parse response
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.debug(f"Got response for {item_name}")
            return soup
        except Exception:
            logger.error("Connection error, retrying in 10 seconds...")
            sleep(10)
            continue
    else:
        logger.critical("Too many connection retries, exiting...")
        raise TooManyConnectionRetries


def setup_logging():
    # Setup logging
    config = {
        'handlers': [
            {'sink': sys.stdout, 'colorize': True, 'level': 'INFO'},
        ]
    }
    logger.configure(**config)


def add_listing(user, id, title, price, url, thumbnail_image, source_image, new, origin_country, postage_fee,
                seller_info):
    if seller_info is not None:
        seller_info = seller_info.split(' ')
        seller_name = seller_info[0]
        items_sold = seller_info[1].replace('(', '').replace(')', '')
        seller_rating = seller_info[2]
    else:
        seller_name, items_sold, seller_rating = None, None, None
    listing = ListingsModel(id=id, name=title, price=price,
                            url=url, date=date.today(), thumbnail=thumbnail_image,
                            source=source_image, new=new, origin_country=origin_country,
                            postage_fee=postage_fee, seller=seller_name,
                            seller_items_sold=items_sold,
                            seller_rating=seller_rating)
    db.session.add(listing)
    user.listings.append(listing)
    db.session.commit()


def init_values(user_id) -> None:
    setup_logging()
    user = UserModel.query.filter_by(id=user_id).first()
    urls = user.urls  # Get all URLs for user

    logger.info(f"Starting eBay scraper for user {user.username}...")
    for url in urls:
        soup = get_soup(url.url, url.name)
        for y in range(20):
            try:
                data = get_attr(soup, y + 1)
                data['id'] = user.chat_id + int(user_id) + int(data['id'])
            except IndexError:
                break
            try:
                add_listing(user, **data)
            except IntegrityError:
                db.session.rollback()
        logger.debug(f"Init {url.url} done!")
    logger.info("Init sqlite database done!")
    logger.info("Starting to check for new listings...")


def scraper(user_id) -> None:
    user = UserModel.query.filter_by(id=user_id).first()
    urls = user.urls  # Get all URLs for user

    chat_id = user.chat_id
    for url in urls:
        # get_soup returns the parsed html of the response
        soup = get_soup(url.url, url.name)
        for y in range(20):
            # Check if the listing y+1 is not out of range
            try:
                data = get_attr(soup, y + 1)
                data['id'] = user.chat_id + int(user_id) + int(data['id'])
            except IndexError:
                break
            try:
                add_listing(user, **data)
                send_message(url.name, data['price'], data['source_image'],
                             data['url'], data['title'], chat_id, data['origin_country'], data['postage_fee'])
                logger.debug("Message sent to Telegram")
                logger.success(
                    f"New listing for {url.name} found! URL: {data['url']}")
                sleep(2)
            except IntegrityError:
                # Listing already exists in database, rollback
                db.session.rollback()


def start_all():
    users = UserModel.query.all()
    for user in users:
        if user.scraper_status:
            logger.info(f"Starting scraper for user {user.username}...")
            scraper_thread = Thread(target=scraper_loop, args=[user.id])
            scraper_thread.start()


if __name__ == '__main__':
    scraper_loop(1)
