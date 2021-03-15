#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================


from urllib import parse

from .common import Color
from .engine_common import CommonEngine


class Google(CommonEngine):
    def __init__(self):
        # CommonEngineの処理を呼出し
        super().__init__()

        self.NAME = 'Google'
        self.COLOR = Color.PURPLE

        # リクエスト先のURLを指定
        self.SEARCH_URL = 'https://www.google.com/search'
        self.SUGGEST_URL = 'http://www.google.com/complete/search'

    def gen_search_url(self, keyword, type):
        # 検索パラメータの設定
        url_param = {
            'q': keyword,        # 検索キーワード
            'num': '100',   # 1ページごとの表示件数
            'filter': '0',  # 類似ページのフィルタリング(0...無効, 1...有効)
            'start': '',    # 開始位置
            'tbs': '',      # 期間
            'nfpr': '1'     # もしかして検索(Escape hatch)を無効化
        }

        # lang/localeが設定されている場合
        if self.LANG and self.LOCALE:
            url_param['hl'] = self.LANG
            url_param['gl'] = self.LOCALE

        # rangeが設定されている場合
        try:
            start = self.RANGE_START
            end = self.RANGE_END

            cd_min = start.strftime("%m/%d/%Y")
            cd_max = end.strftime("%m/%d/%Y")

            # GETパラメータに日時データを追加
            url_param['tbs'] = "cdr:1,cd_min:{0},cd_max:{1}".format(
                cd_min, cd_max)

        except AttributeError:
            None

        page = 0
        while True:
            # parameterにページを開始する番号を指定
            url_param['start'] = str(page * 100)
            params = parse.urlencode(url_param)

            target_url = self.SEARCH_URL + '?' + params

            yield target_url

            page += 1

    def gen_suggest_url(self, keyword):
        url_param = {
            'q': keyword,  # 検索キーワード
            'output': 'toolbar',
            'ie': 'utf-8',
            'oe': 'utf-8',
            'client': 'firefox'
        }

        params = parse.urlencode(url_param)
        url = self.SUGGEST_URL + '?' + params

        return url

    def get_links(self, html, type):
        # Splash経由で通信している場合
        self.SOUP_SELECT_URL = '.ZINbbc > .kCrYT > a'
        self.SOUP_SELECT_TITLE = '.ZINbbc > .kCrYT > a > .zBAuLc > .BNeawe'
        if self.SPLASH_URI != "":
            self.SOUP_SELECT_URL = '.tF2Cxc > .yuRUbf > a'
            self.SOUP_SELECT_TITLE = '.tF2Cxc > .yuRUbf > a > .LC20lb'

        # CommonEngineの処理を呼び出す
        links = super().get_links(html, type)

        return links

    def get_suggest_list(self, suggests, char, html):
        suggests[char if char == '' else char[-1]] = html.json()[1]
        return suggests

    def processings_elist(self, elinks, etitles):
        if self.SPLASH_URI == "":
            new_elinks = []
            for elink in elinks:
                parsed = parse.urlparse(elink)
                parsed_q = parse.parse_qs(parsed.query)['q']  # TODO: チェック処理が必要
                if len(parsed_q) > 0:
                    new_elink = parsed_q[0]
                    new_elinks.append(new_elink)
            elinks = list(dict.fromkeys(new_elinks))

        return elinks, etitles
