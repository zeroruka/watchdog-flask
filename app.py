from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS

from common.errors import errors
from common.models import db
from resources.auth import UserRegistration, UserLogin, ChangePassword, ChangeChatId, GetUserProfile, DeleteUser
from resources.control import Control
from resources.listings import Listing
from resources.admin import GetAllUsers, GetAllListings, AdminDeleteUser, AdminStartAllScraper, GetAllUrls
from resources.url import Url

app = Flask(__name__)
api = Api(app, errors=errors)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
cors = CORS(app, resources={r"/v1/*": {"origins": "*"}})

app.config.from_envvar('ENV_FILE_LOCATION')  # JWT_SECRET_KEY
db.init_app(app)

api_prefix = '/v1'
endpoints = {
    'Url': '/scraper/',
    'Listing': '/listings/',
    'Control': '/control/<string:action>/',
    'UserRegistration': '/register/',
    'UserLogin': '/login/',
    'ChangePassword': '/change-password/',
    'GetUserProfile': '/get-user-profile/',
    'ChangeChatId': '/change-chat-id/',
    'DeleteUser': '/goodbye/',
    'GetAllUsers': '/admin/get-all-users/',
    'GetAllListings': '/admin/get-all-listings/',
    'AdminDeleteUser': '/admin/delete-user/',
    'AdminStartAllScraper': '/admin/start-all-scrapers/',
    'GetAllUrls': '/admin/get-all-urls/',
}

for endpoint, path in endpoints.items():
    api.add_resource(globals()[endpoint], f'{api_prefix}{path}')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5123, debug=True)
