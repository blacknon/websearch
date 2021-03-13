#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import datetime
import re

from urllib import parse
from bs4 import BeautifulSoup

from .common import Color
from .engine_common import CommonEngine


class Bing(CommonEngine):
    def __init__(self):
        # CommonEngineの処理を呼出し
        super().__init__()

        self.NAME = 'Bing'
        self.COLOR = Color.CYAN

        # リクエスト先のURLを指定
        self.SEARCH_URL = 'https://www.bing.com/search'
        self.SUGGEST_URL = 'https://www.bing.com/AS/Suggestions'

    def gen_search_url(self, keyword, type):
        # 検索パラメータの設定
        url_param = {
            'q': keyword,    # 検索キーワード
            'count': '100',  # 1ページごとの表示件数
            'go': '検索',
            'qs': 'ds',
            'from': 'QBRE',
            'filters': '',   # 期間含めフィルターとして指定するパラメータ
            'first': ''      # 開始位置
        }

        # lang/localeが設定されている場合
        if self.LANG and self.LOCALE:
            url_param['mkt'] = self.LANG + '-' + self.LOCALE

        # rangeが設定されている場合
        try:
            start = self.RANGE_START
            end = self.RANGE_END

            unix_day = datetime.strptime('1970-01-01', "%Y-%m-%d")
            cd_min = (start - unix_day).days
            cd_max = (end - unix_day).days

            # GETパラメータに日時データを追加
            url_param['filters'] = 'ex1:"ez5_{0}_{1}"'.format(cd_min, cd_max)

        except AttributeError:
            None

        page = 0
        while True:
            # parameterにページを開始する番号を指定
            url_param['first'] = str(page * 100)
            params = parse.urlencode(url_param)

            target_url = self.SEARCH_URL + '?' + params

            yield target_url

            page += 1

    def gen_suggest_url(self, keyword):
        url_param = {
            'qry': keyword,  # 検索キーワード
            'cvid': 'F5F47E4155E44D86A86690B49023B0EF'
        }

        params = parse.urlencode(url_param)
        url = self.SUGGEST_URL + '?' + params

        return url

    def get_links(self, html, type):
        # Splash経由で通信している場合
        self.SOUP_SELECT_URL = 'h2 > a'
        self.SOUP_SELECT_TITLE = 'h2 > a'

        # CommonEngineの処理を呼び出す
        links = super().get_links(html, type)

        return links

    def get_suggest_list(self, suggests, char, html):
        soup = BeautifulSoup(html.text, 'lxml')
        elements = soup.select('ul > li')
        suggests[char if char == '' else char[-1]] = [e['query']
                                                      for e in elements]
        return suggests

    def processings_elist(self, elinks, etitles):
        new_elinks = list()
        new_etitles = list()

        # `https://rd.listing.yahoo.co.jp/`を除外する
        yahoo_match = re.compile(r'^https://rd\.listing\.yahoo\.co\.jp/')

        n = 0
        for link in elinks:
            if link[0] != '/' and not yahoo_match.match(link):
                new_elinks.append(link)
                if len(etitles) > n:
                    new_etitles.append(etitles[n])
            n += 1

        return new_elinks, new_etitles
