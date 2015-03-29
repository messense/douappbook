#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import multiprocessing
from multiprocessing.pool import ThreadPool
from threading import Lock

import requests
import requests.packages.urllib3 as urllib3
urllib3.contrib.pyopenssl.inject_into_urllib3()


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


def check_proxy(pip, index, total, f, lock):
    logger.info('Checking %d/%d %s', index, total, pip)

    if is_bad_proxy(pip):
        logger.info("Bad Proxy %s", pip)
        return
    logger.info("%s is working", pip)
    with lock:
        f.write(pip + '\n')
        f.flush()


def main():
    with open('proxylist.txt') as f:
        proxy_list = f.readlines()

    f = open('proxy.txt', 'w')
    lock = Lock()
    total = len(proxy_list)
    pool = ThreadPool(multiprocessing.cpu_count() * 2 + 1)
    try:
        for index, proxy in enumerate(proxy_list):
            if proxy.startswith('http://'):
                curr_proxy = proxy.strip()
            else:
                curr_proxy = 'http://%s' % proxy.strip()

            pool.apply_async(
                check_proxy,
                args=(curr_proxy, index, total, f, lock)
            )
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        logger.info('Received control-c, terminating...')
        pool.terminate()
    f.close()


if __name__ == '__main__':
    fmt = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')
    hdlr = logging.StreamHandler()
    hdlr.setFormatter(fmt)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(hdlr)

    main()
