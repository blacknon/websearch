#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================


import json
import re

from urllib import parse
from bs4 import BeautifulSoup

from .common import Color
from .engine_common import CommonEngine


class DuckDuckGo(CommonEngine):
    def __init__(self):
        # CommonEngineの処理を呼出し
        super().__init__()

        self.NAME = 'DuckDuckGo'
        self.COLOR = Color.BLUE

        # リクエスト先のURLを指定
        self.PRE_URL = 'https://duckduckgo.com/'
        self.SEARCH_URL = 'https://links.duckduckgo.com/d.js'
        self.SUGGEST_URL = 'https://duckduckgo.com/ac/'

    def gen_search_url(self, keyword, type):
        # 前処理リクエスト用パラメータの設定
        pre_param = {
            'q': keyword,  # 検索キーワード
            't': 'h_'
        }

        # 検索パラメータの設定
        url_param = {
            'q': keyword,  # 検索キーワード
            's': 0  # 取得開始件数
        }

        # lang/localeが設定されている場合
        if self.LANG and self.LOCALE:
            url_param['l'] = self.LANG + '_' + self.LOCALE

        # rangeが設定されている場合(DuckDuckGoにはレンジ指定がないらしいので、追加されたら記述する)

        try:
            # 前処理リクエスのセッションを生成する
            pre_params = parse.urlencode(pre_param)
            pre_url = self.PRE_URL + '?' + pre_params

            # 前処理リクエスト1を実行
            self.session.get('https://duckduckgo.com/?t=h_')

            # 前処理リクエスト2を実行
            pre_html = self.session.get(
                pre_url,
                headers={'Referer': 'https://duckduckgo.com/'}
            )

            r = re.findall(
                r"(?<=vqd\=)[0-9-]+", pre_html.text
            )

            # get vqd
            vqd = r[0]
            url_param['vqd'] = vqd

        except Exception:
            return

        # set next_url
        params = parse.urlencode(url_param)
        self.next_url = self.SEARCH_URL + '?' + params

        page = 0
        while True:
            if self.next_url == "":
                break

            # get next_url
            target_url = self.next_url

            yield target_url

            page += 1

    def gen_suggest_url(self, keyword):
        url_param = {
            'q': keyword,  # 検索キーワード
            'kl': 'wt-wt'
        }

        params = parse.urlencode(url_param)
        url = self.SUGGEST_URL + '?' + params

        return url

    def get_links(self, html, type):
        links = list()

        # 加工してdictとして扱えるようにする
        r = re.findall(
            r"DDG\.pageLayout\.load\(\'d\',(.+)\]\)\;", html
        )

        try:
            r_dict = json.loads(r[0] + "]")
        except Exception:
            return links

        # next_url用のurl
        url = ""

        for r_data in r_dict:
            if "u" in r_data and "s" in r_data:
                d = {
                    "link": r_data["u"],
                    "title": BeautifulSoup(
                        r_data["t"], "lxml").text
                }
                links.append(d)

            elif "n" in r_data:
                base_uri = '{uri.scheme}://{uri.netloc}'.format(
                    uri=parse.urlparse(self.SEARCH_URL)
                )
                url = base_uri + r_data["n"]

        if url != "":
            self.next_url = url

        return links

    def get_suggest_list(self, suggests, char, html):
        suggests[char if char == '' else char[-1]] = [e['phrase']
                                                      for e in html.json()]
        return suggests
