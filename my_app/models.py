from sqlalchemy import Column, Integer, String, literal
from db import engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from elasticsearch import Elasticsearch
import json
import pymongo
from bson.objectid import ObjectId
import re


Session = sessionmaker(bind=engine)
session = Session()


Base = declarative_base(engine)


# page posts limited number
LIMIT = 10

#Mongo DB
mongo = pymongo.MongoClient("localhost", 27017)
flask_db = mongo.flask
post_tb = flask_db.new_post


# ElasticSearch
class ES():
    def __init__(self):
        hosts = [{'host': 'localhost', 'port': '9200'}]
        self.es = Elasticsearch(
            hosts
            # sniff_on_start=True,
            # sniff_on_connection_fail=True,
            # sniffer_timeout=600,
        )

    def new_index(self, index, id, doc_type, body):
        self.es.index(index=index, doc_type=doc_type, id=id, body=body)

    def postlst_es(self, postlst):
        for post in postlst:
            id = str(post.get('_id'))
            # post = json.loads(post)
            del post['_id']
            self.new_index(index="po", id=id, doc_type="post", body=post)

    def search(self, page, keyword):
        # fuzzy searching
        cnt = self.es.count(body={
            "query": {
                "query_string": {
                    "query": "*" + keyword + "*"
                }
            }
        }).get('count', 1)

        if page <= 0:
            page = 1
        offset = (page - 1) * LIMIT
        if offset >= cnt and offset > LIMIT:
            offset = cnt - LIMIT

        result = self.es.search(body={
            "from": offset, "size": LIMIT,
            "sort": [
                {"_id": "asc"},
            ],
            "query": {
                "query_string": {
                    "query": "*" + keyword + "*"
                }
            }
        })
        # result = self.es.search(body={})

        result_list = result.get('hits').get('hits')
        ret = list()
        for result in result_list:
            content = result.get('_source')
            content['_id'] = result.get('_id')
            ret.append(content)
        # cnt = result.get('hits').get('total')
        page_sum = int(cnt / LIMIT)
        if cnt % LIMIT:
            page_sum += 1

        return ret, page_sum


# es = ES()


class Post:
    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author

    def insert_post(self):
        post_one = {"title": self.title, "content":self.content, "author": self.author}
        post_tb.insert_one(post_one)

    def get_all(self):
        posts = post_tb.find().sort('_id', pymongo.ASCENDING)
        return posts

    @classmethod
    def find_one(cls, id):
        return post_tb.find_one({"_id": ObjectId(id)})
        # return post

    @classmethod
    def find_pagination(cls, page, keyword, limit=LIMIT):

        keyword = re.compile('.*'+keyword+'.*', re.IGNORECASE)
        posts = post_tb.find({"$or":[ {"title": keyword}, {"content": keyword}, {"author": keyword}]}).sort('_id', pymongo.ASCENDING)
        cnt = posts.count()
        if page <= 0:
            page = 1

        offset = (page-1) * limit

        if limit < 0:
            limit = -limit
        if offset >= cnt and cnt > limit:
            offset = cnt - limit

        page_sum = int(cnt / limit)
        if cnt % limit:
            page_sum += 1

        if cnt > 0:
            last_id = posts[offset]['_id']
        else:
            last_id = ""
        # new_posts = post_tb.find({'_id': {'$gte': last_id}}).sort('_id', pymongo.ASCENDING).limit(limit)
        new_posts = post_tb.find({"$and":[{'_id': {'$gte': last_id}}, {"$or":[ {"title": keyword}, {"content": keyword}, {"author": keyword}]}]}).sort('_id', pymongo.ASCENDING).limit(limit)
        return new_posts, page_sum


class User(Base):
    # 定义表名为users
    __tablename__ = 'users'



    # id as primary key
    id = Column(Integer, primary_key=True)

    username = Column(String(50), unique=True)
    password = Column(String(100))
    email = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))


def add_user(username, password, email, first_name, last_name):
    tmp_user = User(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
    try:
        session.add(tmp_user)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()


# if not exist, return false
def check_user(username):
    flag = False
    try:
        for name in session.query(User.username).filter(User.username == username):
            flag = True
    except:
        session.rollback()
    finally:
        session.close()
        return flag


# if not exist, return false
def login_check(username, password):
    flag = False
    try:
        for user in session.query(User).filter(User.username==username, User.password==password):
            flag = True
    except:
        session.rollback()
    finally:
        session.close()
        return flag


Base.metadata.create_all()




