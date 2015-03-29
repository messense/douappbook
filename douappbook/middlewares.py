# -*- coding: utf-8 -*-
import re
import random
import base64

from scrapy import log
from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware as _RetryMiddleware


class RetryMiddleware(_RetryMiddleware):

    def __init__(self, settings):
        super(RetryMiddleware, self).__init__(settings)
        self.proxies = {}
        self.proxy_list = settings.get('PROXY_LIST')
        if not self.proxy_list:
            return

        try:
            with open(self.proxy_list) as f:
                lines = f.readlines()
        except (IOError, EOFError):
            return

        for line in lines:
            parts = re.match('(\w+://)(\w+:\w+@)?(.+)', line)

            # Cut trailing @
            if parts.group(2):
                user_pass = parts.group(2)[:-1]
            else:
                user_pass = ''

            self.proxies[parts.group(1) + parts.group(3)] = user_pass

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        last_proxy = request.meta.get('proxy')
        if last_proxy and self.proxies:
            self.proxies.pop(last_proxy, None)
            log.msg('Removing failed proxy <%s>, %d proxies left' % (
                last_proxy, len(self.proxies))
            )

        if not self.proxies and retries <= self.max_retry_times:
            log.msg(format="Retrying %(request)s (failed %(retries)d times): %(reason)s",
                    level=log.DEBUG, spider=spider, request=request, retries=retries, reason=reason)

            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if self.proxies:
                proxy_address = random.choice(self.proxies.keys())
                proxy_user_pass = self.proxies[proxy_address]
                log.msg('Using proxy <%s>, %d proxies left' % (proxy_address, len(self.proxies)))
                retryreq.meta['proxy'] = proxy_address
                if proxy_user_pass:
                    basic_auth = 'Basic ' + base64.encodestring(proxy_user_pass)
                    retryreq.headers['Proxy-Authorization'] = basic_auth

            return retryreq
        else:
            log.msg(format="Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                    level=log.DEBUG, spider=spider, request=request, retries=retries, reason=reason)
