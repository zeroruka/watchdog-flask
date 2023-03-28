import json

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from common.models import UserModel, ListingsModel
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

        listings = ListingsModel.query.all()
        listings = [listing.serialize() for listing in listings]
        serialized_listings = {}
        for item in listings:
            key = list(item.keys())[0]
            serialized_listings[key] = item[key]
        return serialized_listings


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
        start_all()
        return {"message": "Successfully started all scrapers"}, 200
