import json

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from common.models import UserModel, ListingsModel, UrlModel
from common.scraper import start_all


class GetAllUsers(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=user_id).first()
        if not user.admin:
            return {"message": "Unauthorized"}, 401

        users = UserModel.query.all()
        users = [user.serialize() for user in users]
        serialized_users = {}
        for item in users:
            key = list(item.keys())[0]
            serialized_users[key] = item[key]
        return serialized_users


class GetAllListings(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=user_id).first()
        if not user.admin:
            return {"message": "Unauthorized"}, 401

        serialized_listings = {}
        listings = ListingsModel.query.all()
        # serialize listings based on user_id sort by user_id
        for user in UserModel.query.all():
            userid = user.id
            username = user.username
            serialized_listings[f"{username}_{userid}"] = {}
            for listing in listings:
                if listing.added_by.first().id == userid:
                    serialized_listings[f"{username}_{userid}"].update(
                        listing.serialize())
        return serialized_listings


class GetAllUrls(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=user_id).first()
        if not user.admin:
            return {"message": "Unauthorized"}, 401

        serialized_urls = {}
        urls = UrlModel.query.all()
        # serialize listings based on user_id sort by user_id
        for user in UserModel.query.all():
            userid = user.id
            username = user.username
            serialized_urls[f"{username}_{userid}"] = {}
            for url in urls:
                if url.added_by[0].id == userid:
                    serialized_urls[f"{username}_{userid}"].update(
                        url.serialize())
        return serialized_urls


class AdminDeleteUser(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=user_id).first()
        if not user.admin:
            return {"message": "Unauthorized"}, 401

        data = request.get_json()
        user = UserModel.query.filter_by(id=data.get('user_id')).first()
        user.delete()
        return {"message": f"Successfully deleted user"}, 200


class AdminStartAllScraper(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=user_id).first()
        if not user.admin:
            return {"message": "Unauthorized"}, 401
        # If start_all has been called already, return none
        if start_all():
            return {"message": "Successfully started all scrapers"}, 200
        return {"message": "Scrapers already started"}, 200
