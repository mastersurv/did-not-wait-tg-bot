# from typing import Optional
#
# import asyncpg
# from asyncpg.protocol.protocol import Record
#
# import config
# from database.models import User
#
#
# class Database:
#     def __init__(self):
#         self.pool: Optional[asyncpg.pool.Pool] = None
#
#     async def create_pool(self):
#         try:
#             self.pool = await asyncpg.create_pool(
#                 user=config.DB_USER,
#                 password=config.DB_PASS,
#                 port=config.DB_PORT,
#                 host=config.DB_HOST,
#                 database=config.DB_NAME
#             )
#         except asyncpg.exceptions.InvalidCatalogNameError:
#             # База данных не существует, нужно создать
#             self.pool = await asyncpg.create_pool(
#                 user=config.DB_USER,
#                 password=config.DB_PASS,
#                 port=config.DB_PORT,
#                 host=config.DB_HOST,
#                 database="postgres"
#             )
#             await self.pool.execute(f"CREATE DATABASE {config.DB_NAME}")
#             await self.pool.execute("GRANT ALL ON SCHEMA public TO postgres")
#             await self.pool.close()
#
#             self.pool = await asyncpg.create_pool(
#                 user=config.DB_USER,
#                 password=config.DB_PASS,
#                 port=config.DB_PORT,
#                 host=config.DB_HOST,
#                 database=config.DB_NAME
#             )
#
#     async def _execute(self, command: str, *args,
#                        fetch_all=False, fetch_row=False, fetch_val=False):
#         if self.pool is None:
#             await self.create_pool()
#         async with self.pool.acquire() as connection:
#             connection: asyncpg.Connection
#             async with connection.transaction():
#                 if fetch_all:
#                     result = await connection.fetch(command, *args)
#                 elif fetch_row:
#                     result = await connection.fetchrow(command, *args)
#                 elif fetch_val:
#                     result = await connection.fetchval(command, *args)
#                 else:
#                     result = await connection.execute(command, *args)
#             return result
#
#     # section: Tables creation
#
#     async def _create_table_users(self):
#         query = """
#         CREATE TABLE IF NOT EXISTS users (
#             telegram_id BIGINT PRIMARY KEY,
#             full_name VARCHAR(255) NOT NULL,
#             username VARCHAR(255)
#         )
#         """
#         await self._execute(query)
#
#     async def create_standard_tables(self):
#         await self._create_table_users()
#
#     # section: Static methods
#
#     @staticmethod
#     def get_user_model_from_row_record(user_row_record: Record):
#         return User(
#             telegram_id=user_row_record['telegram_id'],
#             full_name=user_row_record['full_name'],
#             username=user_row_record['username']
#         )
#
#     # section: Working with table users
#
#     ...
#
#     # select example: SELECT
#     #                     count(*)
#     #                 FROM users_statistics
#     #                 WHERE 1=1
#     #                     AND current_timestamp - '1 month'::interval <= action_date
#     #                     AND action = $1
#     # insert example: INSERT INTO users (full_name, username, telegram_id)
#     #                 VALUES ($1, $2, $3)
#     #                 returning *
#     # update example: UPDATE users SET balance = balance + $1
#     #                 WHERE telegram_id = $2
#     #                 returning *
#     # delete example: DELETE FROM custom_buttons
#     #                 WHERE ru_name LIKE '%' || $1 || '%'
#     #                     OR en_name LIKE '%' || $1 || '%'
#     #                 returning *
