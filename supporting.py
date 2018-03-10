# from flask import Flask
# # from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import create_engine,Table,Column,Integer,String,MetaData,ForeignKey
# from db import engine
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'Fianna'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@host:port/dbname'
# app.config['SQLALCHEMY_TRACK_MODIFICATION']
#
# def connect_db():
#
#     with engine.connect() as con:
#         # 先删除users表
#         con.execute('drop table if exists users')
#         # 创建一个users表，有自增长的id和name
#         con.execute('create table users(id int primary key auto_increment,' 'name varchar(25))')
#         # 插入两条数据到表中
#         con.execute('insert into users(name) values("xiaoming")')
#         con.execute('insert into users(name) values("xiaotuo")')
#         # 执行查询操作
#         rs = con.execute('select * from users')
#         # 从查找的结果中遍历
#         for row in rs:
#             print (row)
#
#
# import my_app.views
#
#
# if __name__ == '__main__':
#     app.run()
#
