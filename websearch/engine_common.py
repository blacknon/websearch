#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import requests
import json

# selenium driver auto install packages
import chromedriver_autoinstaller
import geckodriver_autoinstaller

# selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from urllib import parse
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class CommonEngine:
    # Class作成時の処理
    def __init__(self):
        # headless browserの利用有無フラグ(デフォルト: False)
        self.USE_SELENIUM = False
        self.USE_SPLASH = False

        # 初期値の作成
        self.SPLASH_URI = ''
        self.PROXY = ''
        self.USERAGENT = ''

    # 検索エンジンにわたす言語・国の設定を受け付ける
    def set_lang(self, lang, locale):
        self.LANG = lang
        self.LOCALE = locale

    # 検索時の日時範囲を指定I
    def set_range(self, start, end):
        self.RANGE_START = start
        self.RANGE_END = end

    # useragentの設定値を受け付ける(引数がない場合はランダム。Seleniumの際は未使用)
    def set_user_agent(self, user_agent: str = None):
        if user_agent is None:
            ua = UserAgent()
            user_agent = ua.random

        self.USER_AGENT = user_agent

    # seleniumを有効にする
    #   - splashより優先
    #   - host, browserは、指定がない場合はそれぞれデフォルト設定(hostは指定なし、browserはchrome)での動作
    #   - browserは `chrome` or `firefox` のみ受け付ける
    def set_selenium(self, uri: str = None, browser: str = None):
        # TODO: 作る
        # 入力値検証(browser: chrome or firefox)

        # USE_SELENIUM to True
        self.USE_SELENIUM = True
        self.SELENIUM_URI = uri
        self.SELENIUM_BROWSER = browser

        # selenium optionsの作成
        options = Options()
        options.add_argument('--headless')
        self.SELENIUM_OPTIONS = options

    # proxyの設定を受け付ける
    def set_proxy(self, proxy):
        self.PROXY = proxy

    # splash urlの値を受け付ける
    def set_splash(self, splash_url):
        self.USE_SPLASH = True
        self.SPLASH_URI = splash_url

    # selenium driverの作成
    def create_selenium_driver(self):
        # optionsを取得する
        options = self.selenium_options

        # proxyを追加
        if self.PROXY != '':
            options.add_argument('--proxy-server=%s' % self.PROXY)

        # browserに応じてdriverを作成していく
        if self.SELENIUM_BROWSER == 'chrome':
            chromedriver_autoinstaller.install()
            self.driver = webdriver.Chrome(options=options)

        elif self.SELENIUM_BROWSER == 'firefox':
            geckodriver_autoinstaller.install()
            self.driver = webdriver.Firefox(options=options)

        return

    # selenium経由でリクエストを送信する
    def request_selenium(self, url, recaptcha_token=None):
        self.driver.get(url)
        result = self.driver.page_source

        return result

    # splash経由でのリクエストを送信する
    def request_splash(self, url, recaptcha_token=None):
        # urlを生成する
        splash_url = 'http://' + self.SPLASH_URL + '/render.html?'

        # 更にProxy指定もする場合
        if self.PROXY != '':
            proxy = parse.quote_plus(self.PROXY)
            splash_url = splash_url + 'proxy=' + proxy + '&'

        # urlを修正
        url = splash_url + 'url=' + parse.quote_plus(url)

        # リクエストを投げてレスポンスを取得する
        result = self.session.get(url)

        return result

    # seleniumやsplushなどのヘッドレスブラウザ、request.sessionの作成・設定を行う
    def create_session(self):
        # seleniumを使う場合
        if self.USE_SELENIUM:
            self.create_selenium_driver()

        # splashを使う場合
        elif self.USE_SPLASH:
            # create session
            self.session = requests.session()

            # user-agentを設定
            if self.USER_AGENT != '':
                self.session.headers.update(
                    {
                        'User-Agent': self.USER_AGENT,
                        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
                    }
                )

        # requestを使う場合
        else:
            # create session
            self.session = requests.session()

            # proxyを設定
            if self.PROXY != '':
                proxies = {
                    'http': self.PROXY,
                    'https': self.PROXY
                }
                self.session.proxies = proxies

            # user-agentを設定
            if self.USER_AGENT != '':
                self.session.headers.update(
                    {
                        'User-Agent': self.USER_AGENT,
                        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
                    }
                )

        return

    # リクエストを投げてhtmlを取得する(selenium/splash/requestで分岐してリクエストを投げるwrapperとして動作させる)
    def get_result(self, url):
        # 優先度1: Selenium経由でのアクセス
        if self.USE_SELENIUM:
            result = self.request_selenium(url)

        # 優先度2: Splash経由でのアクセス(Seleniumが有効になってない場合はこちら)
        elif self.USE_SPLASH:
            # create splash url
            result = self.request_splash(url)

        # 優先度3: request.sessionからのリクエスト(SeleniumもSplashも有効でない場合)
        else:
            result = self.session.get(url).text

        return result

    # 検索用のurlを生成
    def gen_search_url(self, keyword, type):
        result = {}
        return result

    # テキスト、画像検索の結果からlinksを取得するための集約function
    def get_links(self, html, type):
        # BeautifulSoupでの解析を実施
        soup = BeautifulSoup(html, 'lxml')

        if type == 'text':
            # link, titleの組み合わせを取得する
            elinks, etitles = self.get_text_links(soup)

            # 加工処理を行う関数に渡す(各エンジンで独自対応)
            elinks, etitles = self.processings_elist(elinks, etitles)

            # dictに加工してリスト化する
            # [{'title': 'title...', 'url': 'https://hogehoge....'}, {...}]
            links = self.create_text_links(elinks, etitles)

            return links

        elif type == 'image':
            elinks = self.get_image_links(soup)

    # テキスト検索ページの検索結果(links([{link: ..., title: ...},...]))を生成するfunction
    def get_text_links(self, soup):
        # linkのurlを取得する
        elements = soup.select(self.SOUP_SELECT_URL)
        elinks = [e['href'] for e in elements]

        # linkのtitleを取得する
        elements = soup.select(self.SOUP_SELECT_TITLE)
        etitles = [e.text for e in elements]

        return elinks, etitles

    # 画像検索ページの検索結果(links(list()))を生成するfunction
    def get_image_links(self, soup):
        elements = soup.select(self.SOUP_SELECT_IMAGE)
        jsons = [json.loads(e.get_text()) for e in elements]
        elinks = [js['ou'] for js in jsons]

        return elinks

    # elist, etitle生成時の追加編集処理用function
    def processings_elist(self, elinks, etitles):
        return elinks, etitles

    # テキスト検索の1ページごとの検索結果から、links(links([{link: ..., title: ...},...]))を生成するfunction
    def create_text_links(self, elinks, etitles):
        links = list()
        n = 0
        before_link = ""
        for link in elinks:
            if len(etitles) > n:
                d = {"link": link, "title": etitles[n]}
            else:
                d = {"link": link}

            if before_link != link:
                links.append(d)

            before_link = link
            n += 1
        return links

    # サジェスト取得用のurlを生成
    def gen_suggest_url(self, keyword):
        result = {}
        return result

    # サジェストの取得
    def get_suggest_list(self, html):
        result = {}
        return result
