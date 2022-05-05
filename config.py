import os
basedir = os.path.abspath(__file__)


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	# db connecting
	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:savage@localhost/microblog_db'
	SQLALCHEMY_TRACK_MODIFICATIONS = True