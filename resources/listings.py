from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from flask import request
from sqlalchemy import desc

from common.errors import InternalServerError, UserDoesNotExistError
from common.models import ListingsModel, UserModel, db


class Listing(Resource):
    @jwt_required()
    def get(self):  # Get all listings for user
        args = request.args.get('listing_id', None)
        if args:
            try:
                listing_id = int(args)
                listing = ListingsModel.query.filter_by(id=listing_id).first()
                if listing:
                    return listing.serialize()
                else:
                    return {'message': 'Listing not found'}, 404
            except ValueError:
                return {'message': 'Listing id must be an integer'}, 400
            except Exception:
                raise InternalServerError

        else:
            try:
                user_id = get_jwt_identity()
                user = UserModel.query.filter_by(id=user_id).first()
                listings = user.listings.order_by(
                    desc(ListingsModel.date)).all()
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

    @jwt_required()
    def delete(self):
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
