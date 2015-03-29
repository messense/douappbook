# -*- coding: utf-8 -*-
import os
import sys

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
    def get_book_ids(cls):
        sql = "SELECT id FROM {table}".format(table=cls._table)
        cursor, conn = cls.get_cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cls.close_cursor(cursor)
        ids = [row[0] for row in rows]
        return ids

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
    def get_rating_counts(cls):
        sql = (
            "SELECT book_id,count(id) as rating_count FROM {table}"
            " GROUP BY book_id ORDER BY rating_count ASC"
        ).format(table=cls._table)
        cursor, conn = cls.get_cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cls.close_cursor(cursor)
        return rows

    @classmethod
    def get_book_rating_ids(cls, book_id):
        sql = "SELECT id FROM {table} WHERE book_id=%(book_id)s".format(
            table=cls._table
        )
        data = {'book_id': book_id}
        cursor, conn = cls.get_cursor()
        cursor.execute(sql, data)
        rows = cursor.fetchall()
        cls.close_cursor(cursor)
        rating_ids = [row[0] for row in rows]
        return rating_ids

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


class CrawledBook(BaseModel):
    _table = 'crawled_book'
    _fields = 'book_id,rating_count'

    @classmethod
    def upsert_book(cls, book_id, rating_count=0):
        sql = """REPLACE INTO {table}({fields}) VALUES(
            %(book_id)s,%(rating_count)s
        )""".format(table=cls._table, fields=cls._fields)
        book = {
            'book_id': book_id,
            'rating_count': rating_count,
        }
        cursor, conn = cls.get_cursor()
        cursor.execute(sql, book)
        conn.commit()
        cls.close_cursor(cursor)

    @classmethod
    def get_book(cls, book_id):
        sql = "SELECT {fields} FROM {table} WHERE book_id=%(book_id)s".format(
            table=cls._table,
            fields=cls._fields
        )
        data = {'book_id': book_id}
        cursor, conn = cls.get_cursor()
        cursor.execute(sql, data)
        row = cursor.fetchone()
        cls.close_cursor(cursor)
        if not row:
            return None
        return {'book_id': row[0], 'rating_count': row[1]}

    @classmethod
    def rebuild(cls):
        all_book_ids = Book.get_book_ids()
        rating_counts = Rating.get_rating_counts()
        book_ids = set([r[0] for r in rating_counts])
        for count in rating_counts:
            book_id = count[0]
            rating_count = count[1]
            cls.upsert_book(book_id, rating_count)

        no_rating_ids = all_book_ids - book_ids
        for book_id in no_rating_ids:
            cls.upsert_book(book_id, 0)

    @classmethod
    def get_book_ids(cls):
        sql = "SELECT book_id FROM {table} ORDER BY rating_count ASC".format(
            table=cls._table
        )
        cursor, conn = cls.get_cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cls.close_cursor(cursor)
        ids = [row[0] for row in rows]
        return ids

    @classmethod
    def create_table(cls):
        sql = """CREATE TABLE IF NOT EXISTS {table} (
        book_id BIGINT NOT NULL PRIMARY KEY,
        rating_count INT NOT NULL DEFAULT 0,
        INDEX(rating_count)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        """.format(table=cls._table)
        cursor, conn = cls.get_cursor()
        cursor.execute(sql)
        conn.commit()
        cls.close_cursor(cursor)

if __name__ == '__main__':
    Book.create_table()
    Rating.create_table()
    CrawledBook.create_table()
