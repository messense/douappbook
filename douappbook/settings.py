# -*- coding: utf-8 -*-

# Scrapy settings for douappbook project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import os
import MySQLdb

CURR_PATH = os.path.abspath(os.path.dirname(__file__))
PROJ_PATH = os.path.dirname(CURR_PATH)

BOT_NAME = 'douappbook'

SPIDER_MODULES = ['douappbook.spiders']
NEWSPIDER_MODULE = 'douappbook.spiders'

USER_AGENT = 'api-client/0.1.3 com.douban.frodo/2.4.1 iOS/8.2 iPhone6,2'

DEBUG = True

CONCURRENT_ITEMS = 300
CONCURRENT_REQUESTS = 10

ITEM_PIPELINES = {
    'douappbook.pipelines.DouAppBookPipeline': 300,
}

# Retry many times since proxies often fail
RETRY_TIMES = 10
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 503, 504, 403, 404, 408]

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None,
    'douappbook.middlewares.RetryMiddleware': 100,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
}

# Proxy list containing entries like
# http://host1:port
# http://username:password@host2:port
# http://host3:port
# ...
PROXY_LIST = os.path.join(PROJ_PATH, 'proxy.txt')

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
