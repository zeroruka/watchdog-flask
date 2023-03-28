import datetime

import requests
import os

from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from common.models import UserModel
from common.errors import UserAlreadyExistsError, InternalServerError, UserNotAuthorizedError, NoSuchChatError


def verify_chat_id(field):
    """ field can be chat_id or username """
    token = os.getenv('BOT_TOKEN')
    response = requests.get(f'https://api.telegram.org/bot{token}/getUpdates').json()
    for message in response['result']:
        if 'username' in message['message']['chat']:  # Sometimes username key doesn't exist???
            if field == message['message']['chat']['id'] or field == message['message']['chat']['username']:
                return message['message']['chat']['id']
        elif 'first_name' in message['message']['chat']:
            if field == message['message']['chat']['id'] or field == message['message']['chat']['first_name']:
                return message['message']['chat']['id']
    return None


class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        try:
            chat_id = verify_chat_id(data["account"])
            print(data["account"])
            if not chat_id:
                raise NoSuchChatError
            user = UserModel(
                username=data['username'],
                password=data['password'],
                chat_id=chat_id
            )
            if data["username"] == "admin":  # probably not a good idea to do this
                user.admin = True
            user.hash_password()
            user.save()
            user_id = user.id
            return {
                'message': 'User {} was created'.format(data['username']),
                'id': user_id,
                'chat_id': chat_id
            }, 201
        except NoSuchChatError:
            raise NoSuchChatError
        except IntegrityError:
            raise UserAlreadyExistsError
        except Exception:
            raise InternalServerError


class UserLogin(Resource):
    def post(self):
        try:
            data = request.get_json()
            user = UserModel.query.filter_by(username=data.get('username')).first()
            auth = user.check_password(data.get('password'))
            if not auth:
                raise UserNotAuthorizedError
            expires = datetime.timedelta(days=7)
            access_token = create_access_token(identity=str(user.id), expires_delta=expires)
            return {'token': access_token}, 200
        except AttributeError:
            raise UserNotAuthorizedError
        except UserNotAuthorizedError:
            raise UserNotAuthorizedError
        except Exception:
            raise InternalServerError


class ChangePassword(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=user_id).first()
        if not user.check_password(data.get('old_password')):
            return {'message': 'Old password is incorrect'}, 401
        if data.get('new_password') == data.get('old_password'):
            return {'message': 'New password cannot be the same as old password'}, 400
        user.password = data.get('new_password')
        user.hash_password()
        user.save()
        return {'message': 'Password changed successfully'}, 200


class GetUserProfile(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=user_id).first()
        return {'username': user.username,
                'user_id': user.id,
                'chat_id': user.chat_id,
                'scraper_status': user.scraper_status,
                }, 200


class ChangeChatId(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=user_id).first()
        if not verify_chat_id(data.get('chat_id')):
            return {'message': 'Invalid chat id'}, 400
        user.chat_id = data.get('chat_id')
        user.save()
        return {'message': 'Chat id changed successfully'}, 200


class DeleteUser(Resource):
    @jwt_required()
    def delete(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=user_id).first()
        user.delete()
        return {'message': 'User deleted successfully'}, 200
