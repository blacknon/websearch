#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================


import requests
import sys

from time import sleep
from string import ascii_lowercase, digits
from urllib import parse

from .common import Color
from .engine_google import Google


# SearchEngineへの処理をまとめるClass
class SearchEngine:
    def __init__(self):
        self.session = requests.session()

    def set(self, engine):
        ''' 使用する検索エンジンを指定 '''
        # if engine == 'baidu':
        #     self.ENGINE = Baidu()
        #     return

        # if engine == 'bing':
        #     self.ENGINE = Bing()
        #     return

        # if engine == 'duckduckgo':
        #     self.ENGINE = DuckDuckGo()
        #     return

        if engine == 'google':
            self.ENGINE = Google()
            return

        # if engine == 'yahoo':
        #     self.ENGINE = Yahoo()
        #     return

    def set_lang(self, lang, locale):
        ''' 言語・地域を指定 '''
        self.ENGINE.set_lang(lang, locale)

    def set_range(self, start, end):
        ''' 開始・終了期間を指定 '''
        self.ENGINE.set_range(start, end)

    def set_proxy(self, proxy):
        ''' 検索時のProxyを定義 '''
        proxies = {
            'http': proxy,
            'https': proxy
        }
        self.session.proxies = proxies

    def set_splash_url(self, splash_url):
        self.ENGINE.set_splash_url(splash_url)

    def search(self, keyword, type='text', maximum=100, parallel=False, debug=False, cmd=False):
        ''' 検索 '''
        if cmd is True:
            print(self.ENGINE.NAME, type.capitalize(),
                  'Search:', keyword, file=sys.stderr)
        result, total = [], 0

        # maximumが0の場合、返す値は0個になるのでこのままreturn
        if maximum == 0:
            return result

        # 検索処理の開始
        gen_url = self.ENGINE.gen_search_url(keyword, type)
        while True:
            # リクエスト先のurlを取得
            url = next(gen_url)

            # debug
            if debug is True:
                print(Color.CYAN + '[target_url]' + Color.END, file=sys.stderr)
                print(Color.CYAN + url + Color.END, file=sys.stderr)

            # 検索結果の取得
            html = self.session.get(url).text

            # debug
            if debug is True:
                print(Color.PURPLE + '[Response]' + Color.END, file=sys.stderr)
                print(Color.PURPLE + html + Color.END, file=sys.stderr)

            # 検索結果をパースしてurlリストを取得する
            # TODO(blacknon): recaptchaチェックを追加
            #                 (もしrecaptchaになっていた場合、回避して続きをやるかどうするかの処理についても検討する)
            links = self.ENGINE.get_links(html, type)

            # linksの件数に応じて処理を実施
            if not len(links):
                # commandの場合の出力処理
                if cmd is True:
                    print('-> No more links',
                          self.ENGINE.NAME, file=sys.stderr)

                # loopを抜ける
                break

            # maximumで指定した件数を超える場合、その件数までを追加してloopを抜ける
            elif len(links) > maximum - total:
                result += links[:maximum - total]
                break

            # TODO: bingのときだけ追加する処理として外だしする方法を考える
            elif len(links) < 20 and self.ENGINE.NAME == "Bing":
                # Bingの場合、件数以下でも次のページが表示されてしまうため件数でbreak
                result += links[:maximum - total]
                break

            else:
                result += links
                total += len(links)

            # 連続でアクセスすると問題があるため、3秒待機
            sleep(3)

        return result

    def suggest(self, keyword, jap=False, alph=False, num=False, cmd=False):
        ''' サジェスト取得 '''
        # 文字リスト作成
        chars = ['', ' ']
        chars += [' ' + chr(i) for i in range(12353, 12436)] if jap else []
        chars += [' ' + char for char in ascii_lowercase] if alph else []
        chars += [' ' + char for char in digits] if num else []

        # サジェスト取得
        suggests = {}
        for char in chars:
            word = keyword + char
            url = self.ENGINE.gen_suggest_url(word)
            html = self.session.get(url)
            suggests = self.ENGINE.get_suggest_list(suggests, char, html)

            sleep(0.5)

        return suggests
