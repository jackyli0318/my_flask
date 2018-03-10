from flask import Flask
from sqlalchemy import create_engine,Table,Column,Integer,String,MetaData,ForeignKey
from db import engine
# from flask_cache import Cache

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Fianna'

# cache = Cache(app)

# views
import my_app.views

