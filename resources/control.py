from threading import Thread

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource

from common.errors import InternalServerError, UserDoesNotExistError, \
    InvalidActionError, ScraperNotRunningError, ScraperAlreadyRunningError
from common.models import db, UserModel, UrlModel
from common.scraper import scraper_loop


class Control(Resource):
    @jwt_required()
    def post(self, action):
        try:
            user_id = get_jwt_identity()
            user = UserModel.query.filter_by(id=user_id).first()
            urls = user.urls.all()
            if action == "start":
                if not urls:
                    return {"message": "No urls to scrape"}, 200
                if user.scraper_status:
                    raise ScraperAlreadyRunningError
                user.scraper_status = True
                db.session.commit()
                scraper_thread = Thread(target=scraper_loop, args=[user_id])
                scraper_thread.start()
                return {"message": f"Starting scraper for user {user.username}"}, 200
            elif action == "stop":
                if user.scraper_status:
                    user.scraper_status = False
                    db.session.commit()
                else:
                    raise ScraperNotRunningError
                return {"message": "Stopping scraper"}, 200
            else:
                raise InvalidActionError
        except AttributeError:
            raise UserDoesNotExistError
        except ScraperAlreadyRunningError:
            raise ScraperAlreadyRunningError
        except Exception:
            raise InternalServerError

    @jwt_required()
    def get(self, action):
        try:
            user_id = get_jwt_identity()
            user = UserModel.query.filter_by(id=user_id).first()
            if action == "status":
                if user.scraper_status:
                    return {"message": "Scraper is running",
                            "value": True}, 200
                else:
                    return {"message": "Scraper is not running",
                            "value": False}, 200
            else:
                raise InvalidActionError
        except AttributeError:
            raise UserDoesNotExistError
        except Exception:
            raise InternalServerError
