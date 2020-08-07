import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '78as-UIe3-xjK4-3mcE'