import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2


load_dotenv()


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu le devinera pas'
	token = os.environ.get('token')
	DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///pos.db'
	FLASK_APP = os.environ.get('FLASK_APP')

#connection with bd
Base = declarative_base()
engine = create_engine(Config.DATABASE_URI)
Session = sessionmaker(bind=engine)
session= Session()
