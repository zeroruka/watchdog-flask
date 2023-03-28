from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource

from common.errors import InternalServerError, UserDoesNotExistError
from common.models import UserModel, db


class Listing(Resource):
    @jwt_required()
    def get(self):  # Get all listings for user
        try:
            user_id = get_jwt_identity()
            user = UserModel.query.filter_by(id=user_id).first()
            listings = user.listings.all()
            listings = [listing.serialize() for listing in listings]
            serialized_listings = {}
            for item in listings:
                key = list(item.keys())[0]
                serialized_listings[key] = item[key]
            return serialized_listings
        except AttributeError:
            raise UserDoesNotExistError
        except Exception:
            raise InternalServerError


class ResetListingsDB(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = UserModel.query.filter_by(id=user_id).first()
            listings = user.listings.all()
            for listing in listings:
                db.session.delete(listing)
            db.session.commit()
            return {"message": "Successfully deleted all listings"}, 200
        except AttributeError:
            raise UserDoesNotExistError
        except Exception:
            raise InternalServerError
