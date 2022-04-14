import logging
from typing import Optional

import asyncpg
from asyncpg.protocol.protocol import Record

import config
from database.models import User


class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.pool.Pool] = None

    async def create_pool(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=config.DB_USER,
                password=config.DB_PASS,
                port=config.DB_PORT,
                host=config.DB_HOST,
                database=config.DB_NAME
            )
        except asyncpg.exceptions.InvalidCatalogNameError:
            # База данных не существует, нужно создать
            self.pool = await asyncpg.create_pool(
                user=config.DB_USER,
                password=config.DB_PASS,
                port=config.DB_PORT,
                host=config.DB_HOST,
                database="postgres"
            )
            await self.pool.execute(f"CREATE DATABASE {config.DB_NAME}")
            await self.pool.execute("GRANT ALL ON SCHEMA public TO postgres")
            await self.pool.close()

            self.pool = await asyncpg.create_pool(
                user=config.DB_USER,
                password=config.DB_PASS,
                port=config.DB_PORT,
                host=config.DB_HOST,
                database=config.DB_NAME
            )

    async def _execute(self, command: str, *args,
                       fetch_all=False, fetch_row=False, fetch_val=False):
        if self.pool is None:
            await self.create_pool()
        async with self.pool.acquire() as connection:
            connection: asyncpg.Connection
            async with connection.transaction():
                if fetch_all:
                    result = await connection.fetch(command, *args)
                elif fetch_row:
                    result = await connection.fetchrow(command, *args)
                elif fetch_val:
                    result = await connection.fetchval(command, *args)
                else:
                    result = await connection.execute(command, *args)
            return result

    # section: Tables creation

    async def _create_table_users(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            direction VARCHAR(10) NOT NULL, -- егэ или огэ
            interval INT NOT NULL -- от 1 до 7 включительно
        )
        """
        await self._execute(query)

    async def _create_table_subjects(self):
        query = """
        CREATE TABLE IF NOT EXISTS subjects (
            telegram_id BIGINT NOT NULL,
            subject VARCHAR(100) NOT NULL,
            CONSTRAINT subjects_pk PRIMARY KEY (telegram_id, subject)
        )
        """
        await self._execute(query)

    async def _create_table_tasks(self):
        query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id BIGINT PRIMARY KEY,
            text TEXT NOT NULL,
            variant1 VARCHAR(500) NOT NULL,
            variant2 VARCHAR(500) NOT NULL,
            variant3 VARCHAR(500) NOT NULL,
            right_variant INT NOT NULL, -- 1, 2 или 3
            solution TEXT NOT NULL,
            subject VARCHAR(100) NOT NULL,
            direction VARCHAR(10) NOT NULL, -- егэ или огэ
            subtheme VARCHAR(150) NOT NULL
        )
        """
        await self._execute(query)

    async def create_standard_tables(self):
        await self._create_table_users()
        await self._create_table_subjects()
        await self._create_table_tasks()

    # section: Static methods

    @staticmethod
    def get_user_model(user_row_record: Record, subjects: list[str]):
        return User(
            telegram_id=user_row_record['telegram_id'],
            full_name=user_row_record['full_name'],
            direction=user_row_record['direction'],
            interval=user_row_record['interval'],
            subjects=subjects
        )

    # section: Working with table users

    async def add_user(self, telegram_id: int, full_name: str, direction: str, interval: str,
                       subjects: list[str]) -> bool:
        query = "INSERT INTO users (telegram_id, full_name, direction, interval) " \
                "VALUES ($1, $2, $3, $4)"
        try:
            await self._execute(query, telegram_id, full_name, direction, interval)
        except Exception:
            # такой пользователь уже есть в таблице
            return False
        query = "INSERT INTO subjects (telegram_id, subject) VALUES ($1, $2)"
        for subject in subjects:
            try:
                await self._execute(query, telegram_id, subject)
            except Exception as err:
                logging.error(f"Возникла ошибка при создании пользователя {telegram_id}: {err}")
        return True

    async def get_user(self, telegram_id: int) -> User | None:
        query = "SELECT telegram_id, full_name, direction, interval FROM users WHERE telegram_id = $1"
        user_row = await self._execute(query, telegram_id, fetch_row=True)
        if user_row is None:
            return None

        query = "SELECT subject FROM subjects WHERE telegram_id = $1"
        subjects_rows = await self._execute(query, telegram_id, fetch_all=True)
        subjects: list[str] = [subject_row['subject'] for subject_row in subjects_rows]
        return self.get_user_model(user_row, subjects)

    async def user_id_present(self, telegram_id: int) -> bool:
        query = "SELECT telegram_id FROM users WHERE telegram_id = $1"
        return await self._execute(query, telegram_id, fetch_val=True) is not None

    # select example: SELECT
    #                     count(*)
    #                 FROM users_statistics
    #                 WHERE 1=1
    #                     AND current_timestamp - '1 month'::interval <= action_date
    #                     AND action = $1
    # insert example: INSERT INTO users (full_name, username, telegram_id)
    #                 VALUES ($1, $2, $3)
    #                 returning *
    # update example: UPDATE users SET balance = balance + $1
    #                 WHERE telegram_id = $2
    #                 returning *
    # delete example: DELETE FROM custom_buttons
    #                 WHERE ru_name LIKE '%' || $1 || '%'
    #                     OR en_name LIKE '%' || $1 || '%'
    #                 returning *
