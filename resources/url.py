from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from common.errors import InternalServerError, UrlAlreadyExistsError, UrlDoesNotExistError, UserDoesNotExistError
from common.models import UrlModel, db, UserModel

# URL Arguments
url_put_args = reqparse.RequestParser()
url_put_args.add_argument("name", type=str, help="Name of the url")
url_put_args.add_argument(
    "url", type=str, help="Url is required", required=True)


class Url(Resource):
    @jwt_required()
    def get(self):  # Get all urls
        try:
            user_id = get_jwt_identity()  # Get user id from JWT
            user = UserModel.query.filter_by(
                id=user_id).first()  # Get user from database
            urls = user.urls  # Get all urls for user
            urls = [url.serialize() for url in urls]  # Serialize urls
            serialized_urls = {}
            for url in urls:
                key = list(url.keys())[0]
                serialized_urls[key] = url[key]
            return serialized_urls
        except AttributeError:
            raise UserDoesNotExistError
        except Exception:
            raise InternalServerError

    @jwt_required()
    def put(self):  # Add url
        try:
            user_id = get_jwt_identity()
            user = UserModel.query.filter_by(id=user_id).first()
            args = url_put_args.parse_args()

            url = args['url']
            url = url.strip()  # Remove whitespace from url
            url = url.replace(" ", "+")
            url = f"https://www.ebay.com.sg/sch/i.html?_from=R40&_nkw={url}&_sacat=0&_sop=10&_ipg=120"

            # Check if url already exists
            result = user.urls.filter(UrlModel.url == url).first()
            if result:
                raise UrlAlreadyExistsError
            url = UrlModel(name=args['name'], url=url)  # Create new url
            db.session.add(url)  # Add url to database
            user.urls.append(url)  # Add relation between user and url
            db.session.commit()
            return {"message": f"Successfully added {url}"}, 201
        except AttributeError:
            raise UserDoesNotExistError
        except UrlAlreadyExistsError:
            raise UrlAlreadyExistsError
        except Exception:
            raise InternalServerError

    @jwt_required()
    def delete(self):  # Delete url
        try:
            user_id = get_jwt_identity()
            user = UserModel.query.filter_by(id=user_id).first()

            args = url_put_args.parse_args()
            result = user.urls.filter(UrlModel.url == args['url']).first()
            db.session.delete(result)  # Delete url from database
            db.session.commit()
            return {"message": f"Successfully deleted {result}"}, 200
        except AttributeError:
            raise UserDoesNotExistError
        except (AttributeError, Exception):
            raise UrlDoesNotExistError
        except Exception:
            raise InternalServerError
