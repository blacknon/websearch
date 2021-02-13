#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import asyncio
import requests


# コンソール出力時に色付をするためのClass
class Color:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[1;30m'
    END = '\033[0m'
    BOLD = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE = '\033[07m'


# dictやlistから重複要素を除外する
def get_unique_list(seq):
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]


# リダイレクトするurlリストから遷移先のURLを取得するfunction
async def resolv_links(loop, session, links):
    ''' リダイレクト先のurlをパラレルで取得する(Baiduで使用) '''
    async def req(session, url):
        task = await loop.run_in_executor(None, resolv_url, session, url)
        return task

    tasks = []
    for link in links:
        task = req(session, link)
        tasks.append(task)

    data = await asyncio.gather(*tasks)

    return data


# リダイレクトするurlから遷移先のURLを取得するfunction
def resolv_url(session, url):
    ''' リダイレクト先のurlを取得する(Baiduで使用) '''
    try:
        res_header = session.head(url, allow_redirects=False).headers
    except requests.RequestException:
        return url
    except ConnectionError:
        return url
    else:
        url = res_header['Location']
    return url
