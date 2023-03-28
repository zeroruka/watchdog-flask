class InternalServerError(Exception):
    pass

class TooManyConnectionRetries(Exception):
    pass

class UrlAlreadyExistsError(Exception):
    pass

class UrlDoesNotExistError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class UserDoesNotExistError(Exception):
    pass

class UserNotAuthorizedError(Exception):
    pass

class UserNotLoggedInError(Exception):
    pass

class ScraperAlreadyRunningError(Exception):
    pass

class ScraperNotRunningError(Exception):
    pass

class InvalidActionError(Exception):
    pass

class NoSuchChatError(Exception):
    pass


errors = {
    'InternalServerError': {
        'message': 'Internal server error',
        'status': 500
    },
    'TooManyConnectionRetries': {
        'message': 'Too many connection retries',
        'status': 500
    },
    'UrlAlreadyExistsError': {
        'message': 'Url already exists',
        'status': 400
    },
    'UrlDoesNotExistError': {
        'message': 'Url does not exist',
        'status': 400
    },
    'UserAlreadyExistsError': {
        'message': 'User already exists',
        'status': 402
    },
    'UserDoesNotExistError': {
        'message': 'User does not exist',
        'status': 400
    },
    'UserNotAuthorizedError': {
        'message': 'User not authorized',
        'status': 401
    },
    'ScraperAlreadyRunningError': {
        'message': 'Scraper already running',
        'status': 400
    },
    'ScraperNotRunningError': {
        'message': 'Scraper not running',
        'status': 400
    },
    'InvalidActionError': {
        'message': 'Invalid action',
        'status': 400
    },
    'NoSuchChatError': {
        'message': 'No such chat',
        'status': 401
    }
}

