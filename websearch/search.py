#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2019 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import requests
import json
import sys
import re
from string import ascii_lowercase, digits
from urllib import parse
from time import sleep
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from .common import Color


# SearchEngineへの処理をまとめるClass
class SearchEngine:

    def __init__(self):
        # generate UserAgent
        ua = UserAgent()
        useragent = ua.random

        # 事前に初期化しておく
        self.SPLASH_URL = ''

        # requests.sessionの作成
        self.session = requests.session()
        self.session.headers.update(
            {'User-Agent': useragent}
        )

    def set(self, engine):
        ''' サーチエンジンごとの設定 '''
        # Bing
        if engine == 'bing':
            self.ENGINE = 'Bing'
            self.SEARCH_URL = 'https://www.bing.com/search'
            self.SUGGEST_URL = 'https://www.bing.com/AS/Suggestions'
            self.TEXT_PARAM = {
                'q': '',
                'count': '100',
                'filter': '0',
                'ia': 'web',
                'first': ''
            }
            self.IMAGE_PARAM = {
                'q': '',
                'tbm': 'isch',
                'filter': '0',
                'ia': 'web',
                'ijn': ''
            }
            self.SUGGEST_PARAM = {
                'qry': '',
                'cvid': 'F5F47E4155E44D86A86690B49023B0EF'
            }
            self.SOUP_SELECT_TEXT = 'li > h2 > a'
            self.SOUP_SELECT_IMAGE = '.rg_meta.notranslate'
            return

        # DuckDuckGo

        # Google
        if engine == 'google':
            self.ENGINE = 'Google'
            self.SEARCH_URL = 'https://www.google.co.jp/search'
            self.SUGGEST_URL = 'http://www.google.co.jp/complete/search'
            self.TEXT_PARAM = {
                'q': '',
                'num': '100',
                'filter': '0',
                'start': ''
            }
            self.IMAGE_PARAM = {
                'q': '',
                'tbm': 'isch',
                'filter': '0',
                'ijn': ''
            }
            self.SUGGEST_PARAM = {
                'q': '',
                'output': 'toolbar',
                'ie': 'utf-8',
                'oe': 'utf-8',
                'client': 'firefox'
            }
            self.SOUP_SELECT_TEXT = '.rc > .r > a'
            self.SOUP_SELECT_IMAGE = '.rg_meta.notranslate'
            return

        # Yahoo
        # NOTE: Yahoo.co.jpでは1ページごとの表示件数を指定できないため、複数のGETリクエストが飛んでしまう
        # TODO(blacknon): 作成中
        if engine == 'yahoo':
            self.ENGINE = 'Yahoo'
            self.SEARCH_URL = 'https://search.yahoo.co.jp/search'
            self.SUGGEST_URL = 'https://assist-search.yahooapis.jp/SuggestSearchService/V5/webassistSearch'
            self.TEXT_PARAM = {
                'p': '',
                'num': '100',  # 指定不可(削除)
                'filter': '0',
                'b': ''  # 次のページの数
            }
            self.IMAGE_PARAM = {
                'q': '',
                'tbm': 'isch',
                'filter': '0',
                'ijn': ''
            }
            self.SUGGEST_PARAM = {
                'query': '',
                # ↓正常に動作しなくなった場合はブラウザからアクセスして更新！ (TODO:自動取得処理の追加)
                'appid': 'dj0zaiZpPVU5MGlSOUZ4cHVLbCZzPWNvbnN1bWVyc2VjcmV0Jng9ZGQ-',
                'output': 'json',
            }
            self.SOUP_SELECT_TEXT = 'h3 > a'
            self.SOUP_SELECT_IMAGE = '.rg_meta.notranslate'
            return

    def set_proxy(self, proxy):
        proxies = {
            'http': proxy,
            'https': proxy
        }
        self.session.proxies = proxies

    def search(self, keyword, type='text', maximum=100, parallel=False, debug=False):
        ''' 検索 '''
        print(self.ENGINE, type.capitalize(),
              'Search:', keyword, file=sys.stderr)
        result, total = [], 0
        query = self.query_gen(keyword, type)

        if maximum == 0:
            return

        while True:
            q = next(query)

            # debug
            if debug is True:
                print(Color.CYAN +
                      '[target_url]' + Color.END, file=sys.stderr)
                print(Color.CYAN + q + Color.END, file=sys.stderr)

            # 検索
            html = self.session.get(q).text
            links = self.get_links(html, type)

            # debug
            if debug is True:
                print(Color.PURPLE +
                      '[Response]' + Color.END, file=sys.stderr)
                print(Color.PURPLE + html +
                      Color.END, file=sys.stderr)

            # 検索結果の追加
            if not len(links):
                print('-> No more links', self.ENGINE, file=sys.stderr)
                break
            elif len(links) > maximum - total:
                result += links[:maximum - total]
                break
            else:
                result += links
                total += len(links)
            sleep(0.5)

        print('-> Finally got', str(len(result)),
              'links', self.ENGINE, file=sys.stderr)
        return result

    def suggest(self, keyword, jap=False, alph=False, num=False):
        ''' サジェスト取得 '''
        # 文字リスト作成
        chars = ['', ' ']
        chars += [' ' + chr(i) for i in range(12353, 12436)] if jap else []
        chars += [' ' + char for char in ascii_lowercase] if alph else []
        chars += [' ' + char for char in digits] if num else []

        # サジェスト取得
        suggests = {}
        for char in chars:
            if self.ENGINE == 'Bing':  # Bing
                self.SUGGEST_PARAM['qry'] = keyword + char
                params = parse.urlencode(self.SUGGEST_PARAM)

                # レスポンスを取得
                res = self.session.get(self.SUGGEST_URL + '?' + params)
                soup = BeautifulSoup(res.text, 'lxml')
                elements = soup.select('ul > li')
                suggests[char if char == '' else char[-1]] = [e['query']
                                                              for e in elements]

            elif self.ENGINE == 'Google':  # Google
                self.SUGGEST_PARAM['q'] = keyword + char
                params = parse.urlencode(self.SUGGEST_PARAM)

                # レスポンスを取得
                res = self.session.get(self.SUGGEST_URL + '?' + params)
                suggests[char if char == '' else char[-1]] = res.json()[1]

            elif self.ENGINE == 'Yahoo':  # Yahoo
                self.SUGGEST_PARAM['query'] = keyword + char
                params = parse.urlencode(self.SUGGEST_PARAM)

                # レスポンスを取得
                res = self.session.get(self.SUGGEST_URL + '?' + params)
                data = json.loads(res.text)
                suggests[char if char == '' else char[-1]] = [e['Suggest']
                                                              for e in data['Result']]

            sleep(0.5)
        return suggests

    def query_gen(self, keyword, type):
        ''' 検索クエリの生成 '''
        page = 0
        while True:
            if type == 'text':
                if self.ENGINE == 'Bing':
                    self.TEXT_PARAM['q'] = keyword
                    self.TEXT_PARAM['first'] = str(page * 100)

                elif self.ENGINE == 'Google':
                    self.TEXT_PARAM['q'] = keyword
                    self.TEXT_PARAM['start'] = str(page * 100)

                elif self.ENGINE == 'Yahoo':
                    self.TEXT_PARAM['p'] = keyword
                    self.TEXT_PARAM['b'] = str(page * 10)

                params = parse.urlencode(self.TEXT_PARAM)

            elif type == 'image':
                self.IMAGE_PARAM['q'] = keyword
                self.IMAGE_PARAM['ijn'] = str(page * 100)
                params = parse.urlencode(self.IMAGE_PARAM)

            target_url = self.SEARCH_URL + '?' + params

            # Splashの有無に応じてURLを変更
            if self.SPLASH_URL != '':
                target_url = self.SPLASH_URL + parse.quote(target_url)

            yield target_url
            page += 1

    def get_links(self, html, type):
        ''' html内のリンクを取得 '''
        soup = BeautifulSoup(html, 'lxml')
        if type == 'text':
            elements = soup.select(self.SOUP_SELECT_TEXT)
            elinks = [e['href'] for e in elements]
        elif type == 'image':
            elements = soup.select(self.SOUP_SELECT_IMAGE)
            jsons = [json.loads(e.get_text()) for e in elements]
            elinks = [js['ou'] for js in jsons]

        # `translate.google.co.jp`を除外して配列に代入
        links = list()
        for link in elinks:
            if not re.match(r"^https://translate.google.co.jp", link):
                links.append(link)

        return links
