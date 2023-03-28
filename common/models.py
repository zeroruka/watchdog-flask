from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash

db = SQLAlchemy()


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    scraper_status = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    chat_id = db.Column(db.Integer, nullable=True)  # Telegram chat id

    listings = db.relationship('ListingsModel', secondary='user_listings', back_populates='added_by', lazy='dynamic')
    urls = db.relationship('UrlModel', secondary='user_urls', backref='added_by', lazy='dynamic')

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            self.id: {
                'username': self.username,
                'scraper_status': self.scraper_status,
                'admin': self.admin,
                'chat_id': self.chat_id
            }
        }

    def __repr__(self):
        return str(self.serialize())


class ListingsModel(db.Model):
    __tablename__ = 'listings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    url = db.Column(db.String(100), nullable=False)

    thumbnail = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(100), nullable=False)

    date = db.Column(db.Date, nullable=False)
    new = db.Column(db.Boolean, nullable=True)

    seller = db.Column(db.String(100), nullable=True)
    seller_items_sold = db.Column(db.Integer, nullable=True)
    seller_rating = db.Column(db.String(10), nullable=True)

    origin_country = db.Column(db.String(100), nullable=True)
    postage_fee = db.Column(db.String(100), nullable=True)

    added_by = db.relationship('UserModel', secondary='user_listings', back_populates='listings', lazy='dynamic')

    def serialize(self):
        return {
            self.id: {
                'listing': {
                    'title': self.name,
                    'price': self.price,
                    'url': self.url,
                    'date_added': str(self.date),
                    'new': self.new,
                    'origin_country': self.origin_country,
                    'postage_fee': self.postage_fee,
                    'images': {
                        'thumbnail_l225px': self.thumbnail,
                        'source_l800px': self.source
                    }
                },
                'seller': {
                    'name': self.seller,
                    'items_sold': self.seller_items_sold,
                    'rating': self.seller_rating
                },
            }
        }

    def __repr__(self):
        return f"Listing(name = {self.name}, price = {self.price}, url = {self.url}, date = {self.date})"


class UrlModel(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200))

    def serialize(self):
        return {
            self.id: {
                'name': self.name,
                'url': self.url,
                'added_by': str(self.added_by)
            }
        }

    def __repr__(self):
        return f"Url(id = {self.id} name = {self.name}, url = {self.url})"


user_listings = db.Table('user_listings',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                         db.Column('listing_id', db.Integer, db.ForeignKey('listings.id'), primary_key=True)
                         )

# Secondary table to map the relationships between users and urls
user_urls = db.Table('user_urls',
                     db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                     db.Column('url_id', db.Integer, db.ForeignKey('urls.id'), primary_key=True)
                     )
