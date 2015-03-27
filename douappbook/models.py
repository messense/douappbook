# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime

if __name__ == '__main__':
    curr_path = os.path.abspath(os.path.dirname(__file__))
    proj_path = os.path.dirname(curr_path)
    sys.path.append(proj_path)

import scrapy

from douappbook.settings import db_conn


class BaseModel(object):
    _table = ''
    _fields = ''

    @classmethod
    def get_cursor(cls):
        return db_conn.cursor(), db_conn

    @classmethod
    def close_cursor(cls, cursor):
        cursor.close()

    @classmethod
    def create_table(cls):
        raise NotImplementedError()


class Book(BaseModel):
    _table = 'book'
    _fields = 'id,title,author,url,cover,rating,rating_count'

    @classmethod
    def upsert_book(cls, book):
        if isinstance(book, scrapy.Item):
            book = dict(book)
        sql = """REPLACE INTO {table}({fields}) VALUES(
            %(id)s,%(title)s,%(author)s,%(url)s,%(cover)s,
            %(rating)s,%(rating_count)s
        )""".format(table=cls._table, fields=cls._fields)
        cursor, conn = cls.get_cursor()
        cursor.execute(sql, book)
        conn.commit()
        cls.close_cursor(cursor)

    @classmethod
    def create_table(cls):
        sql = """CREATE TABLE IF NOT EXISTS {table}(
        id BIGINT NOT NULL PRIMARY KEY,
        title VARCHAR(256) NOT NULL,
        author VARCHAR(128) NOT NULL,
        url VARCHAR(256) NOT NULL,
        cover VARCHAR(256) NOT NULL,
        rating FLOAT NOT NULL DEFAULT 0,
        rating_count INT NOT NULL DEFAULT 0,
        INDEX(rating),
        INDEX(rating_count),
        INDEX(author)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        """.format(table=cls._table)
        cursor, conn = cls.get_cursor()
        cursor.execute(sql)
        conn.commit()
        cls.close_cursor(cursor)


class Rating(BaseModel):
    _table = 'rating'
    _fields = 'id,book_id,user_id,username,rating,vote,comment'

    @classmethod
    def upsert_rating(cls, rating):
        if isinstance(rating, scrapy.Item):
            rating = dict(rating)
        sql = """REPLACE INTO {table}({fields}) VALUES(
            %(id)s,%(book_id)s,%(user_id)s,%(username)s,
            %(rating)s,%(vote)s,%(comment)s
        )""".format(table=cls._table, fields=cls._fields)
        cursor, conn = cls.get_cursor()
        cursor.execute(sql, rating)
        conn.commit()
        cls.close_cursor(cursor)

    @classmethod
    def create_table(cls):
        sql = """CREATE TABLE IF NOT EXISTS {table} (
        id BIGINT NOT NULL PRIMARY KEY,
        book_id BIGINT NOT NULL,
        user_id BIGINT NOT NULL,
        username VARCHAR(128) NOT NULL,
        rating FLOAT NOT NULL,
        vote INT NOT NULL DEFAULT 0,
        comment VARCHAR(700) NULL,
        INDEX(book_id),
        INDEX(user_id),
        INDEX(rating),
        INDEX(vote)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        """.format(table=cls._table)
        cursor, conn = cls.get_cursor()
        cursor.execute(sql)
        conn.commit()
        cls.close_cursor(cursor)


if __name__ == '__main__':
    Book.create_table()
    Rating.create_table()
