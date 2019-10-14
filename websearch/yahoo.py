#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2019 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import sys

from .search import SearchEngine
from .common import Color


# yahooでの検索
def search(args):
    # google class
    yahoo = SearchEngine()
    yahoo.set('yahoo')

    # proxy
    if args.proxy != '':
        yahoo.set_proxy(args.proxy)

    # Splush
    # TODO(blacknon): Proxyへの対応
    if args.splash != '':
        yahoo.SPLASH_URL = 'http://' + args.splash + '/render.html?url='

    # Header
    header = '[YahooSearch]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = Color.YELLOW + header + Color.END

    # 検索タイプを設定(テキスト or 画像)
    search_type = 'text'
    if args.image:
        print('Sorry, Now development.', file=sys.stderr)  # debug
        exit()  # debug
        search_type = 'image'

    # Yahoo検索を実行
    result = yahoo.search(args.query, type=search_type,
                          maximum=args.num, debug=args.debug)

    # debug
    if args.debug:
        print(Color.GRAY, file=sys.stderr)
        print(result, file=sys.stderr)
        print(Color.END, file=sys.stderr)

    # sep
    sep = ''
    if args.nullchar:
        sep = '\0'

    # 検索結果を出力
    for d in result:
        link = d['link']
        if args.title and 'title' in d:
            title = d['title']
            title = title + ": "

            # titleの色指定
            if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
                title = Color.GRAY + title + Color.END

            print(header + sep + title + sep + link)
        else:
            print(header + sep + link)


# yahooでのsuggest取得
def suggest(args):
    # engine
    yahoo = SearchEngine()
    yahoo.set('yahoo')

    # header
    header = '[YahooSuggest]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = Color.YELLOW + header + Color.END

    # GoogleでのSuggestを取得
    result = yahoo.suggest(
        args.query,
        jap=args.jap,
        alph=args.alph,
        num=args.num
    )
    for words in result.values():
        for w in words:
            print(header + w)
