# -*- coding: utf-8 -*-

# Scrapy settings for douappbook project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'douappbook'

SPIDER_MODULES = ['douappbook.spiders']
NEWSPIDER_MODULE = 'douappbook.spiders'

USER_AGENT = 'api-client/0.1.3 com.douban.frodo/2.4.1 iOS/8.2 iPhone6,2'

DEBUG = True

try:
    from local_settings import *
except ImportError:
    pass
