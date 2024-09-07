# class Config:
#     SECRET_KEY = 'supersecretkey'  
#     SQLALCHEMY_DATABASE_URI = (
#         'mysql+mysqlconnector://'
#         'rafaelharthopf1:sua_senha@rafaelharthopf1.mysql.pythonanywhere-services.com/'
#         'rafaelharthopf1$ecommerce_db'
#     )
#     SQLALCHEMY_TRACK_MODIFICATIONS = False  
class Config:
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:sua_senha@localhost/ecommerce_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
