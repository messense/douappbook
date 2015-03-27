#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import socket
import logging
import multiprocessing
from multiprocessing.pool import ThreadPool


logger = logging.getLogger('proxychecker')


def is_bad_proxy(pip):
    try:
        proxy_handler = urllib2.ProxyHandler({'https': pip})
        opener = urllib2.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        req = urllib2.Request('https://frodo.douban.com:443/api/v2/')
        urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        logger.error('Error code: %s', e.code)
        return e.code
    except Exception, detail:
        logger.error('Error: %s', detail)
        return True
    return False


def check_proxy(pip, index, total):
    logger.info('Checking %d/%d %s', index, total, pip)

    if is_bad_proxy(pip):
        logger.info("Bad Proxy %s", pip)
        return None
    logger.info("%s is working", pip)
    return 'https://' + pip


def main():
    good_proxys = []
    socket.setdefaulttimeout(10)
    with open('proxylist.txt') as f:
        proxy_list = f.readlines()

    total = len(proxy_list)
    pool = ThreadPool(multiprocessing.cpu_count() * 2 + 1)
    async_results = []
    for index, proxy in enumerate(proxy_list):
        if proxy.startswith('http://'):
            curr_proxy = proxy[7:].strip()
        else:
            curr_proxy = proxy.strip()

        async_results.append(pool.apply_async(
            check_proxy,
            args=(curr_proxy, index, total)
        ))
    pool.close()
    pool.join()

    for result in async_results:
        proxy = result.get()
        if proxy:
            good_proxys.append(proxy)

    if not good_proxys:
        print 'No proxy are working!'
        return

    with open('proxy.txt', 'w') as f:
        for proxy in good_proxys:
            f.write(proxy + '\n')

if __name__ == '__main__':
    fmt = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')
    hdlr = logging.StreamHandler()
    hdlr.setFormatter(fmt)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(hdlr)

    main()
