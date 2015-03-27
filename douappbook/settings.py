# -*- coding: utf-8 -*-

# Scrapy settings for douappbook project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import MySQLdb

BOT_NAME = 'douappbook'

SPIDER_MODULES = ['douappbook.spiders']
NEWSPIDER_MODULE = 'douappbook.spiders'

USER_AGENT = 'api-client/0.1.3 com.douban.frodo/2.4.1 iOS/8.2 iPhone6,2'

DEBUG = True

ITEM_PIPELINES = {
    'douappbook.pipelines.DouAppBookPipeline': 300,
}

DB_CONF = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': '',
    'db': 'douappbook',
    'charset': 'utf8',
}

try:
    from local_settings import *
except ImportError:
    pass

db_conn = MySQLdb.connect(
    host=DB_CONF['host'],
    port=DB_CONF.get('port', 3306),
    user=DB_CONF['user'],
    passwd=DB_CONF['passwd'],
    db=DB_CONF['db'],
    charset=DB_CONF.get('charset', 'utf8'),
)
