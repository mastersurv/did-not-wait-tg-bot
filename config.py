from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS", subcast=int)
IP = env.str("IP")
#
# DB_USER = env.str("DB_USER", "postgres")
# DB_PASS = env.str("DB_PASS", "postgres")
# DB_NAME = env.str("DB_NAME")
# DB_HOST = env.str("DB_HOST", "localhost")
# DB_PORT = env.str("DB_PORT", "5432")

REDIS_HOST = env.str("REDIS_HOST", "localhost")
