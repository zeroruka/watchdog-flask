import unittest

from app import app, db


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
        self.app.testing = True

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
