from sqlalchemy import create_engine

# 数据库的配置变量
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'flask'
USERNAME = 'jacky'
PASSWORD = 'jacky'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(USERNAME,PASSWORD,HOSTNAME,PORT,DATABASE)
# "mysql+pymysql://root:@localhost:3306/test",echo=True

# 创建数据库引擎
engine = create_engine(DB_URI, echo=True)

#创建连接
with engine.connect() as con:
    print("Database connected successfully!")
    # rs = con.execute('SELECT 1')
    # print (rs.fetchone())
