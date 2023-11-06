class Config:
    SECRET_KEY = "Our_secret_key"
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://g4t4:password@spm-g4t4-live.cybxkypjkirc.ap-southeast-2.rds.amazonaws.com:3306/sbrp_new"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://g4t4:password@spmg4t4.cybxkypjkirc.ap-southeast-2.rds.amazonaws.com:3306/sbrp_test"
