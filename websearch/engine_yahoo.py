#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================


import json

from urllib import parse
from bs4 import BeautifulSoup

from .common import Color
from .engine_common import CommonEngine


class Yahoo(CommonEngine):
    def __init__(self):
        # CommonEngineの処理を呼出し
        super().__init__()

        self.NAME = 'Yahoo'
        self.COLOR = Color.YELLOW

        # リクエスト先のURLを指定
        self.SEARCH_URL = 'https://search.yahoo.co.jp/search'
        self.SUGGEST_URL = 'https://assist-search.yahooapis.jp/SuggestSearchService/V5/webassistSearch'

    def gen_search_url(self, keyword, type):
        # 検索パラメータの設定
        url_param = {
            'p': keyword,         # 検索キーワード
            'num': '100',    # 指定不可(削除)
            'day_from': '',  # 開始日時(yyyy/mm/dd)
            'day_to': '',    # 終了日時(yyyy/mm/dd)
            'b': '',         # 開始位置
            'nfpr': '1',     # もしかして検索(Escape hatch)の無効化
            'qrw': '0'       # もしかして検索(Escape hatch)の無効化
        }

        # lang/localeが設定されている場合
        if self.LANG and self.LOCALE:
            url_param['hl'] = self.LANG
            url_param['gl'] = self.LOCALE

        # rangeが設定されている場合
        try:
            start = self.RANGE_START
            end = self.RANGE_END

            # ex.) day_from=2019/09/01&day_to=2019/09/30
            # パラメータが2つ存在している
            day_from = start.strftime("%Y/%m/%d")
            day_to = end.strftime("%Y/%m/%d")

            # GETパラメータに日時データを追加
            url_param['day_from'] = day_from
            url_param['day_to'] = day_to

        except AttributeError:
            None

        page = 0
        while True:
            # parameterにページを開始する番号を指定
            url_param['b'] = str(page * 10)
            params = parse.urlencode(url_param)

            target_url = self.SEARCH_URL + '?' + params

            yield target_url

            page += 1

    def gen_suggest_url(self, keyword):
        url_param = {
            'query': keyword,   # 検索キーワード
            # ↓正常に動作しなくなった場合はブラウザからアクセスして更新！ (TODO:自動取得処理の追加)
            'appid': 'dj0zaiZpPVU5MGlSOUZ4cHVLbCZzPWNvbnN1bWVyc2VjcmV0Jng9ZGQ-',
            'output': 'json',
        }

        params = parse.urlencode(url_param)
        url = self.SUGGEST_URL + '?' + params

        return url

    def get_links(self, html, type):
        if self.SPLASH_URL != "":
            self.SOUP_SELECT_JSON = '#__NEXT_DATA__'
            self.SOUP_SELECT_IMAGE = '.rg_meta.notranslate'

            # Yahooの場合、jsonから検索結果を取得する
            soup = BeautifulSoup(html, 'lxml')
            elements = soup.select(self.SOUP_SELECT_JSON)
            element = elements[0].string

            # jsonからデータを抽出　
            j = json.loads(element)
            jd = j['props']['pageProps']['initialProps']['pageData']['algos']

            elinks = [e['url'] for e in jd]
            etitles = [e['title'] for e in jd]

            links = self.create_text_links(elinks, etitles)

        else:
            self.SOUP_SELECT_URL = 'ol > li > a'
            self.SOUP_SELECT_TITLE = 'ol > li > a'

            # CommonEngineの処理を呼び出す
            links = super().get_links(html, type)

        return links

    def get_suggest_list(self, suggests, char, html):
        data = json.loads(html.text)
        suggests[char if char == '' else char[-1]] = [e['Suggest']
                                                      for e in data['Result']]

        return suggests
