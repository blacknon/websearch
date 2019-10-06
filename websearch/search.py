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
        # Baidu
        if engine == 'baidu':
            self.ENGINE = 'Baidu'
            self.SEARCH_URL = 'https://www.baidu.com/s'
            self.SUGGEST_URL = 'https://www.baidu.com/sugrec'
            self.TEXT_PARAM = {
                'wd': '',  # 検索キーワード
                'rn': '50',
                'filter': '0',
                'ia': 'web',
                'pn': ''  # 開始位置
            }
            self.IMAGE_PARAM = {
                'wd': '',  # 検索キーワード
                'tbm': 'isch',
                'filter': '0',
                'ia': 'web',
                'ijn': ''
            }
            self.SUGGEST_PARAM = {
                'wd': '',  # 検索キーワード
                'prod': 'pc'
            }
            self.SOUP_SELECT_URL = '.result > .t > a'
            self.SOUP_SELECT_TITLE = '.result > .t > a'
            self.SOUP_SELECT_IMAGE = '.rg_meta.notranslate'
            return

        # Bing
        if engine == 'bing':
            self.ENGINE = 'Bing'
            self.SEARCH_URL = 'https://www.bing.com/search'
            self.SUGGEST_URL = 'https://www.bing.com/AS/Suggestions'
            self.TEXT_PARAM = {
                'q': '',  # 検索キーワード
                'count': '100',
                'filter': '0',
                'ia': 'web',
                'first': ''  # 開始位置
            }
            self.IMAGE_PARAM = {
                'q': '',  # 検索キーワード
                'tbm': 'isch',
                'filter': '0',
                'ia': 'web',
                'ijn': ''  # 開始位置
            }
            self.SUGGEST_PARAM = {
                'qry': '',  # 検索キーワード
                'cvid': 'F5F47E4155E44D86A86690B49023B0EF'
            }
            self.SOUP_SELECT_URL = 'li > h2 > a'
            self.SOUP_SELECT_TITLE = 'li > h2 > a'
            self.SOUP_SELECT_IMAGE = '.rg_meta.notranslate'
            return

        # DuckDuckGo

        # Google
        if engine == 'google':
            self.ENGINE = 'Google'
            self.SEARCH_URL = 'https://www.google.co.jp/search'
            self.SUGGEST_URL = 'http://www.google.co.jp/complete/search'
            self.TEXT_PARAM = {
                'q': '',  # 検索キーワード
                'num': '100',
                'filter': '0',
                'start': ''  # 開始位置
            }
            self.IMAGE_PARAM = {
                'q': '',  # 検索キーワード
                'tbm': 'isch',
                'filter': '0',
                'ijn': ''  # 開始位置
            }
            self.SUGGEST_PARAM = {
                'q': '',  # 検索キーワード
                'output': 'toolbar',
                'ie': 'utf-8',
                'oe': 'utf-8',
                'client': 'firefox'
            }
            self.SOUP_SELECT_URL = '.rc > .r > a'
            self.SOUP_SELECT_TITLE = '.rc > .r > a > .LC20lb > .ellip'
            self.SOUP_SELECT_IMAGE = '.rg_meta.notranslate'
            return

        # Yahoo
        # NOTE:
        #   yahoo.co.jpでは1ページごとの表示件数を指定できないため、他の検索エンジンに比べて複数のGETリクエストが飛んでしまう
        if engine == 'yahoo':
            self.ENGINE = 'Yahoo'
            self.SEARCH_URL = 'https://search.yahoo.co.jp/search'
            self.SUGGEST_URL = 'https://assist-search.yahooapis.jp/SuggestSearchService/V5/webassistSearch'
            self.TEXT_PARAM = {
                'p': '',  # 検索キーワード
                'num': '100',  # 指定不可(削除)
                'filter': '0',
                'b': ''  # 開始位置
            }
            self.IMAGE_PARAM = {
                'q': '',  # 検索キーワード
                'tbm': 'isch',
                'filter': '0',
                'ijn': ''  # 開始位置
            }
            self.SUGGEST_PARAM = {
                'query': '',  # 検索キーワード
                # ↓正常に動作しなくなった場合はブラウザからアクセスして更新！ (TODO:自動取得処理の追加)
                'appid': 'dj0zaiZpPVU5MGlSOUZ4cHVLbCZzPWNvbnN1bWVyc2VjcmV0Jng9ZGQ-',
                'output': 'json',
            }
            self.SOUP_SELECT_URL = 'h3 > a'
            self.SOUP_SELECT_TITLE = 'h3 > a'
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

            # debug
            if debug is True:
                print(Color.PURPLE +
                      '[Response]' + Color.END, file=sys.stderr)
                print(Color.PURPLE + html +
                      Color.END, file=sys.stderr)

            # 検索結果をパース処理する
            links = self.get_links(html, type)

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
            if self.ENGINE == 'Baidu':  # Baidu
                self.SUGGEST_PARAM['wd'] = keyword + char
                params = parse.urlencode(self.SUGGEST_PARAM)

                # レスポンスを取得
                res = self.session.get(self.SUGGEST_URL + '?' + params)
                if 'g' in res.json():
                    suggests[char if char == '' else char[-1]
                             ] = [e['q']
                                  for e in res.json()['g']]

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

    def resolv_url(self, url):
        ''' リダイレクト先のurlを取得する '''
        try:
            res_header = self.session.head(url, allow_redirects=False).headers
        except requests.RequestException:
            return url
        except ConnectionError:
            return url
        else:
            url = res_header['Location']
            return url

    def query_gen(self, keyword, type):
        ''' 検索クエリの生成 '''
        page = 0
        while True:
            if type == 'text':
                if self.ENGINE == 'Baidu':
                    self.TEXT_PARAM['wd'] = keyword
                    self.TEXT_PARAM['pn'] = str(page * 50)

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
            # linkのurlを取得する
            elements = soup.select(self.SOUP_SELECT_URL)
            elinks = [e['href'] for e in elements]

            # linkのtitleを取得する
            elements = soup.select(self.SOUP_SELECT_TITLE)
            etitles = [e.text for e in elements]

        elif type == 'image':
            elements = soup.select(self.SOUP_SELECT_IMAGE)
            jsons = [json.loads(e.get_text()) for e in elements]
            elinks = [js['ou'] for js in jsons]

        # dictをlistに入れていく
        links = list()
        n = 0
        for link in elinks:
            # もし検索エンジンがBaiduだった場合、linkのリダイレクトを追う
            if self.ENGINE == 'Baidu':
                link = self.resolv_url(link)

            # `translate.google.co.jp`のURLを削除していく(Google翻訳のページ)
            if not re.match(r"^https://translate.google.co.jp", link):
                if len(etitles) > n:
                    d = {"link": link, "title": etitles[n]}
                else:
                    d = {"link": link}
                links.append(d)
                n += 1

        return links
