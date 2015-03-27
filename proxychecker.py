#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import multiprocessing
from multiprocessing.pool import ThreadPool

import requests
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopensslpyopenssl.inject_into_urllib3()


logger = logging.getLogger('proxychecker')


def is_bad_proxy(pip):
    try:
        proxies = {
            'http': pip,
            'https': pip
        }
        requests.get(
            'https://frodo.douban.com:443/api/v2/',
            proxies=proxies,
            timeout=10
        )
    except requests.RequestException as e:
        logger.error('Error: %s', e.message)
        return True
    except Exception as detail:
        logger.error('Error: %s', detail)
        return True
    return False


def check_proxy(pip, index, total):
    logger.info('Checking %d/%d %s', index, total, pip)

    if is_bad_proxy(pip):
        logger.info("Bad Proxy %s", pip)
        return None
    logger.info("%s is working", pip)
    return pip


def main():
    good_proxys = []
    with open('proxylist.txt') as f:
        proxy_list = f.readlines()

    total = len(proxy_list)
    pool = ThreadPool(multiprocessing.cpu_count() * 2 + 1)
    async_results = []
    for index, proxy in enumerate(proxy_list):
        if proxy.startswith('http://'):
            curr_proxy = proxy.strip()
        else:
            curr_proxy = 'http://%s' % proxy.strip()

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
