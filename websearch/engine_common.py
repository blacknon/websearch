#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import requests
import json
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class CommonEngine:
    def __init__(self):
        self.SPLASH_URL = ''
        self.session = requests.session()

    def set_lang(self, lang, locale):
        self.LANG = lang
        self.LOCALE = locale

    def set_range(self, start, end):
        self.RANGE_START = start
        self.RANGE_END = end

    def set_useragent(self, useragent: str = None):
        if useragent is None:
            ua = UserAgent()
            useragent = ua.random

        self.session.header.update(
            {
                'User-Agent': useragent,
                'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
            }
        )

    def set_splash_url(self, splash_url):
        self.SPLASH_URL = splash_url

    def gen_search_url(self, keyword, type):
        result = {}
        return result

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

    def get_text_links(self, soup):
        # linkのurlを取得する
        elements = soup.select(self.SOUP_SELECT_URL)
        elinks = [e['href'] for e in elements]

        # linkのtitleを取得する
        elements = soup.select(self.SOUP_SELECT_TITLE)
        etitles = [e.text for e in elements]

        return elinks, etitles

    def get_image_links(self, soup):
        elements = soup.select(self.SOUP_SELECT_IMAGE)
        jsons = [json.loads(e.get_text()) for e in elements]
        elinks = [js['ou'] for js in jsons]

        return elinks

    def processings_elist(self, elinks, etitles):
        return elinks, etitles

    def create_text_links(self, elinks, etitles):
        links = list()
        n = 0
        for link in elinks:
            if len(etitles) > n:
                d = {"link": link, "title": etitles[n]}
            else:
                d = {"link": link}
            links.append(d)
            n += 1
        return links

    def gen_suggest_url(self, keyword):
        result = {}
        return result

    # サジェストの取得
    def get_suggest_list(self, html):
        result = {}
        return result
