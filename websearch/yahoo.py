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
    if args.color == 'always':
        header = Color.YELLOW + header + Color.END
    elif args.color == 'auto' and sys.stdout.isatty():
        header = Color.YELLOW + header + Color.END

    # 検索タイプを設定(テキスト or 画像)
    search_type = 'text'
    if args.image:
        print('Sorry, Now development in', file=sys.stderr)  # debug
        exit()  # debug
        search_type = 'image'

    # Google検索を実行
    result = yahoo.search(args.query, type=search_type,
                          maximum=args.num, debug=args.debug)
    for link in result:
        print(header + link)


# yahooでの検索
def suggest(args):
    # engine
    yahoo = SearchEngine()
    yahoo.set('yahoo')

    # header
    header = '[YahooSuggest]: '
    if args.color == 'always':
        header = Color.YELLOW + header + Color.END
    elif args.color == 'auto' and sys.stdout.isatty():
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
