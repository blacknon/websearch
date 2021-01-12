#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2020 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

# TODO(blacknon): スクレイピングではなく、APIを介しての検索をオプションで指定できるようにする
# TODO(blacknon): BANされた時にわかるようにする(errを返すようにしたい)
# TODO(blacknon): ブラウザのCookieを共有する方法について考える(re-captcha対策)
#                 => ブラウザからre-captchaをさせられないかという検討。
#                 => おそらく雑に共有はできなそう。import/exportを組み合わせる方法で対応するのが良いか。
# TODO(blacknon): bingの出力が変わってるかも？debugして確認する


import asyncio
import requests
import json
import sys
import re
from string import ascii_lowercase, digits
from datetime import datetime
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
        # TODO(blacknon): Headerをoption等で切り替えできるようにする
        self.session = requests.session()
        self.session.headers.update(
            {
                'User-Agent': useragent,
                'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
            }
        )

    def set(self, engine):
        ''' サーチエンジンごとの設定 '''
        # Baidu
        if engine == 'baidu':
            self.ENGINE = 'Baidu'
            self.SEARCH_URL = 'https://www.baidu.com/s'
            self.SUGGEST_URL = 'https://www.baidu.com/sugrec'
            self.TEXT_PARAM = {
                'wd': '',       # 検索キーワード
                'rn': '50',     # 1ページごとの表示件数
                'filter': '0',  # aaa
                'ia': 'web',    #
                'pn': ''        # 開始位置
            }
            self.IMAGE_PARAM = {
                'wd': '',       # 検索キーワード
                'tbm': 'isch',  #
                'filter': '0',  #
                'ia': 'web',    #
                'ijn': ''       #
            }
            self.SUGGEST_PARAM = {
                'wd': '',      # 検索キーワード
                'prod': 'pc'   #
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
                'q': '',         # 検索キーワード
                'count': '100',  # 1ページごとの表示件数
                'filters': '',   # 期間含めフィルターとして指定するパラメータ
                'first': ''      # 開始位置
            }
            self.IMAGE_PARAM = {
                'q': '',        # 検索キーワード
                'filters': '',  #
                'ijn': ''       # 開始位置
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
        #   ※ DuckDuckGoの場合、検索結果の取得方法が特殊なため作りが少々異なる
        if engine == 'duckduckgo':
            self.ENGINE = 'DuckDuckGo'
            self.PRE_URL = 'https://duckduckgo.com/'
            self.SEARCH_URL = 'https://links.duckduckgo.com/d.js'
            self.SUGGEST_URL = 'https://duckduckgo.com/ac/'
            self.TEXT_PARAM = {
                'q': '',  # 検索キーワード
                's': 0  # 取得開始件数
            }
            self.SUGGEST_PARAM = {
                'q': '',      # 検索キーワード
                'kl': 'wt-wt'   #
            }

        # Google
        if engine == 'google':
            self.ENGINE = 'Google'
            self.SEARCH_URL = 'https://www.google.com/search'
            self.SUGGEST_URL = 'http://www.google.com/complete/search'
            self.TEXT_PARAM = {
                'q': '',        # 検索キーワード
                'num': '100',   # 1ページごとの表示件数
                'filter': '0',  # 類似ページのフィルタリング(0...無効, 1...有効)
                'start': '',    # 開始位置
                'tbs': '',      # 期間
                'nfpr': '1'     # もしかして検索(Escape hatch)を無効化
            }
            self.IMAGE_PARAM = {
                'q': '',        # 検索キーワード
                'tbm': 'isch',  # 検索の種類(isch...画像)
                'filter': '0',  # 類似ページのフィルタリング(0...無効, 1...有効)
                'ijn': '',      # 開始位置
                'tbs': ''       # 期間
            }
            self.SUGGEST_PARAM = {
                'q': '',  # 検索キーワード
                'output': 'toolbar',
                'ie': 'utf-8',
                'oe': 'utf-8',
                'client': 'firefox'
            }
            self.SOUP_SELECT_URL = '.rc > .yuRUbf > a'
            self.SOUP_SELECT_TITLE = '.rc > .yuRUbf > a > .LC20lb'
            self.SOUP_SELECT_IMAGE = '.rg_meta.notranslate'

        # Yahoo
        # NOTE:
        #   yahoo.co.jpでは1ページごとの表示件数を指定できないため、他の検索エンジンに比べて複数のGETリクエストが飛んでしまう
        if engine == 'yahoo':
            self.ENGINE = 'Yahoo'
            self.SEARCH_URL = 'https://search.yahoo.co.jp/search'
            self.SUGGEST_URL = 'https://assist-search.yahooapis.jp/SuggestSearchService/V5/webassistSearch'
            self.TEXT_PARAM = {
                'p': '',         # 検索キーワード
                'num': '100',    # 指定不可(削除)
                'day_from': '',  # 開始日時(yyyy/mm/dd)
                'day_to': '',    # 終了日時(yyyy/mm/dd)
                'b': '',         # 開始位置
                'nfpr': '1',     # もしかして検索(Escape hatch)の無効化
                'qrw': '0'       # もしかして検索(Escape hatch)の無効化
            }
            self.IMAGE_PARAM = {
                'q': '',        # 検索キーワード
                'tbm': 'isch',  #
                'filter': '0',  #
                'ijn': ''       # 開始位置
            }
            self.SUGGEST_PARAM = {
                'query': '',   # 検索キーワード
                # ↓正常に動作しなくなった場合はブラウザからアクセスして更新！ (TODO:自動取得処理の追加)
                'appid': 'dj0zaiZpPVU5MGlSOUZ4cHVLbCZzPWNvbnN1bWVyc2VjcmV0Jng9ZGQ-',
                'output': 'json',
            }
            self.SOUP_SELECT_URL = '.Contents__innerGroupBody > .sw-CardBase > .Algo > section > .sw-Card__section > .sw-Card__headerSpace > .sw-Card__title > a'  # NOT WORKING
            self.SOUP_SELECT_TITLE = '.Contents__innerGroupBody > .sw-CardBase > .Algo > section > .sw-Card__section > .sw-Card__headerSpace > .sw-Card__title > a > h3'  # NOT WORKING
            self.SOUP_SELECT_JSON = '#__NEXT_DATA__'
            self.SOUP_SELECT_IMAGE = '.rg_meta.notranslate'
            return

        # Yandex
        # TODO(blacknon): Yandexの追加
        # if engine == 'yandex':
        #     self.ENGINE = 'Yandex'

    def set_lang(self, lang, locale):
        ''' 国・言語を検索エンジンごとのパラメータに適用する '''
        if self.ENGINE == 'Baidu':
            None

        if self.ENGINE == 'Bing':
            self.TEXT_PARAM['mkt'] = lang + '-' + locale

        if self.ENGINE == 'DuckDuckGo':
            self.TEXT_PARAM['l'] = lang + '_' + locale

        if self.ENGINE == 'Google':
            self.TEXT_PARAM['hl'] = lang
            self.TEXT_PARAM['gl'] = locale
            None

        if self.ENGINE == 'Yahoo':
            self.TEXT_PARAM['hl'] = lang
            self.TEXT_PARAM['gl'] = locale

    def set_range(self, start, end):
        ''' 開始・終了期間を検索エンジンごとのパラメータに適用する '''

        # Baidu
        if self.ENGINE == 'Baidu':
            None
            return

        # Bing
        if self.ENGINE == 'Bing':
            # ex.) filters=ex1:"ez5_18170_18174"
            # ※ 1970-01-01からの日数で計測されている
            # 日付を取得する
            unix_day = datetime.strptime('1970-01-01', "%Y-%m-%d")
            cd_min = (start - unix_day).days
            cd_max = (end - unix_day).days

            # GETパラメータに日時データを追加
            self.TEXT_PARAM['filters'] = 'ex1:"ez5_{0}_{1}"'.format(
                cd_min, cd_max)

            return

        # DuckDuckGo
        if self.ENGINE == 'DuckDuckGo':
            # TODO(blacknon):
            #     2020-11-22 現在、日付を指定しての検索クエリ機能がなさそうだ。
            #     追加されたら実装する。
            None

        # Google
        if self.ENGINE == 'Google':
            # ex.) tbs=cdr:1,cd_min:10/1/2019,cd_max:10/31/2019
            # 日付をGoogle検索のフォーマットに書き換える
            cd_min = start.strftime("%m/%d/%Y")
            cd_max = end.strftime("%m/%d/%Y")

            # GETパラメータに日時データを追加
            self.TEXT_PARAM['tbs'] = "cdr:1,cd_min:{0},cd_max:{1}".format(
                cd_min, cd_max)

            return

        # Yahoo
        if self.ENGINE == 'Yahoo':
            # ex.) day_from=2019/09/01&day_to=2019/09/30
            # パラメータが2つ存在している
            day_from = start.strftime("%Y/%m/%d")
            day_to = end.strftime("%Y/%m/%d")

            # GETパラメータに日時データを追加
            self.TEXT_PARAM['day_from'] = day_from
            self.TEXT_PARAM['day_to'] = day_to

            return

    # proxyをセットする
    def set_proxy(self, proxy):
        ''' 検索時のProxyを定義 '''
        proxies = {
            'http': proxy,
            'https': proxy
        }
        self.session.proxies = proxies

    # cookie.txtを読み込んでセットする
    # def set_cookie(self, cookie):
        # None

    # 検索を実行する
    def search(self, keyword, type='text', maximum=100, parallel=False, debug=False, start=None, end=None, cmd=False):
        ''' 検索 '''
        if cmd is True:
            print(self.ENGINE, type.capitalize(),
                  'Search:', keyword, file=sys.stderr)
        result, total = [], 0

        # maximumが0の場合、返す値は0個になるのでこのままreturn
        if maximum == 0:
            return

        # 期間(start, end)が指定されている場合、各検索エンジンの該当パラメータに追加する
        if start is not None and end is not None:
            self.set_range(start, end)

        # DuckDuckGoの場合、通常の検索結果取得とは異なるため分岐
        if self.ENGINE == 'DuckDuckGo':
            # 前処理URLを生成してTokenを取得する
            self.TEXT_PARAM['q'] = keyword
            params = parse.urlencode(self.TEXT_PARAM)
            res = self.session.get(self.PRE_URL + '?' + params)
            r = re.findall(
                r"(?<=vqd\=)[0-9-]+", res.text
            )

            # get vqd
            vqd = r[0]
            self.TEXT_PARAM['vqd'] = vqd

            try:
                query = self.query_gen(keyword, type)
                result = self.__search_duckduckgo(query, maximum, debug=debug)
            except Exception:
                return

        # Baidu, Bing, Google, Yahooの場合
        else:
            query = self.query_gen(keyword, type)
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
                    # TODO(blacknon): recaptchaチェックを追加
                    #                 (もしrecaptchaになっていた場合、回避して続きをやるかどうするかの処理についても検討する)

                    if cmd is True:
                        print('-> No more links', self.ENGINE, file=sys.stderr)
                    break

                elif len(links) > maximum - total:
                    result += links[:maximum - total]
                    break

                elif len(links) < 20 and self.ENGINE == "Bing":
                    # Bingの場合、件数以下でも次のページが表示されてしまうため件数でbreak
                    result += links[:maximum - total]
                    break

                else:
                    result += links
                    total += len(links)
                sleep(0.5)

        if cmd is True:
            print('-> Finally got', str(len(result)),
                  'links', self.ENGINE, file=sys.stderr)

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

            elif self.ENGINE == 'DuckDuckGo':  # DuckDuckGo
                self.SUGGEST_PARAM['q'] = keyword + char
                params = parse.urlencode(self.SUGGEST_PARAM)

                # レスポンスを取得
                res = self.session.get(self.SUGGEST_URL + '?' + params)
                suggests[char if char == '' else char[-1]] = [e['phrase']
                                                              for e in res.json()]

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
            # テキスト検索
            if type == 'text':
                if self.ENGINE == 'Baidu':
                    self.TEXT_PARAM['wd'] = keyword
                    self.TEXT_PARAM['pn'] = str(page * 50)

                if self.ENGINE == 'Bing':
                    self.TEXT_PARAM['q'] = keyword
                    self.TEXT_PARAM['first'] = str(page * 100)

                if self.ENGINE == 'DuckDuckGo':
                    self.TEXT_PARAM['q'] = keyword

                elif self.ENGINE == 'Google':
                    self.TEXT_PARAM['q'] = keyword
                    self.TEXT_PARAM['start'] = str(page * 100)

                elif self.ENGINE == 'Yahoo':
                    self.TEXT_PARAM['p'] = keyword
                    self.TEXT_PARAM['b'] = str(page * 10)

                # パラメータをURLエンコード
                params = parse.urlencode(self.TEXT_PARAM)

            # イメージ検索(いまのところ動作させてない)
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
            if self.ENGINE == 'Yahoo':
                # Yahooの場合、jsonを取得するようになったため分岐
                elements = soup.select(self.SOUP_SELECT_JSON)
                element = elements[0].string

                # jsonからデータを抽出　
                j = json.loads(element)
                jd = j['props']['pageProps']['initialProps']['pageData']['algos']

                elinks = [e['url'] for e in jd]
                etitles = [e['title'] for e in jd]

            else:
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

        # もし検索エンジンがBaiduだった場合、linkのリダイレクトを追う(asyncを利用した非同期処理)
        if self.ENGINE == 'Baidu':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            elinks = loop.run_until_complete(
                resolv_links(loop, self.session, elinks))

        # dictをlistに入れていく
        links = list()
        n = 0
        for link in elinks:
            # `translate.google.co.jp`のURLを削除していく(Google翻訳のページ)
            if not re.match(r"^https://translate.google.co.jp", link) and not re.match(r"^http://cache.yahoofs.jp", link):
                if len(etitles) > n:
                    d = {"link": link, "title": etitles[n]}
                else:
                    d = {"link": link}
                links.append(d)
                n += 1

        return links

    def __search_duckduckgo(self, query, maximum, debug=False):
        '''
          DuckDuckGoの検索用関数
            - DuckDuckGoはJavascriptで検索結果を取得し、さらに前処理でTokenが必要になるためちょっとめんどくさい。
            - なので別関数を用意。
            - 初回のqueryはSearchEngine.query_genで生成する
        '''
        url = next(query)
        links = list()
        while True:
            # debug
            if debug is True:
                print(Color.CYAN + '[target_url]' + Color.END, file=sys.stderr)
                print(Color.CYAN + url + Color.END, file=sys.stderr)

            # 検索結果(javascriptのコード)を取得
            js_text = self.session.get(url).text

            # 加工してdictとして扱えるようにする
            r = re.findall(
                r"DDG\.pageLayout\.load\(\'d\',(.+)\]\)\;", js_text
            )
            try:
                r_dict = json.loads(r[0]+"]")
            except Exception:
                break

            # urlを空にする
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

            if url == "":
                break

            if len(links) >= maximum:
                break

            sleep(0.5)

        if len(links) > maximum:
            links = links[:maximum]

        return links


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


async def resolv_links(loop, session, links):
    ''' リダイレクト先のurlをパラレルで取得する(Baiduで使用) '''
    async def req(session, url):
        return await loop.run_in_executor(None, resolv_url, session, url)

    tasks = [req(session, link) for link in links]
    return await asyncio.gather(*tasks)
