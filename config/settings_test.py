from config.settings import *

DATABASES = {
    'default': env.db("DATABASE_URL"),
}

DATABASE_ROUTERS = []
