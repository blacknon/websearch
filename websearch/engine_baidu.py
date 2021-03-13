#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import asyncio
import requests

from urllib import parse

from . import common
from .common import Color
from .engine_common import CommonEngine


class Baidu(CommonEngine):
    def __init__(self):
        # CommonEngineの処理を呼出し
        super().__init__()

        self.NAME = 'Baidu'
        self.COLOR = Color.RED

        # リクエスト先のURLを指定
        self.SEARCH_URL = 'https://www.baidu.com/s'
        self.SUGGEST_URL = 'https://www.baidu.com/sugrec'

    def gen_search_url(self, keyword, type):
        # 検索パラメータの設定
        url_param = {
            'wd': keyword,  # 検索キーワード
            'rn': '50',     # 1ページごとの表示件数
            'filter': '0',  # aaa
            'ia': 'web',    #
            'pn': ''        # 開始位置
        }

        page = 0
        while True:
            # parameterにページを開始する番号を指定
            url_param['pn'] = str(page * 50)
            params = parse.urlencode(url_param)

            target_url = self.SEARCH_URL + '?' + params

            yield target_url

            page += 1

    def gen_suggest_url(self, keyword):
        url_param = {
            'wd': keyword,  # 検索キーワード
            'prod': 'pc'   #
        }

        params = parse.urlencode(url_param)
        url = self.SUGGEST_URL + '?' + params

        return url

    def get_links(self, html, type):
        # Splash経由で通信している場合
        self.SOUP_SELECT_URL = '.result > .t > a'
        self.SOUP_SELECT_TITLE = '.result > .t > a'

        # CommonEngineの処理を呼び出す
        links = super().get_links(html, type)

        return links

    def get_suggest_list(self, suggests, char, html):
        if 'g' in html.json():
            suggests[char if char == '' else char[-1]
                     ] = [e['q']
                          for e in html.json()['g']]
        return suggests

    def processings_elist(self, elinks, etitles):
        # セッションを作成
        session = requests.session()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        elinks = loop.run_until_complete(
            common.resolv_links(loop, session, elinks))
        loop.close()

        return elinks, etitles
