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


# TODO(blacknon): 検索結果の件数を取得し、その件数までurlを取得したら処理を停止させる(url超過してもリクエストを投げ続けるバグの修正)


# bingでの検索
def search(args):
    # engine
    bing = SearchEngine()
    bing.set('bing')

    # proxy
    if args.proxy != '':
        bing.set_proxy(args.proxy)

    # Splush
    # TODO(blacknon): Proxyへの対応
    if args.splash != '':
        bing.SPLASH_URL = 'http://' + args.splash + '/render.html?url='

    # Header
    header = '[BingSearch]: '
    if args.color == 'always':
        header = Color.CYAN + header + Color.END
    elif args.color == 'auto' and sys.stdout.isatty():
        header = Color.CYAN + header + Color.END

    # 検索タイプを設定(テキスト or 画像)
    search_type = 'text'
    if args.image:
        print('Sorry, Now development in', file=sys.stderr)  # debug
        exit()  # debug
        search_type = 'image'

    # Bingでの検索を実行
    result = bing.search(args.query, type=search_type,
                         maximum=args.num, debug=args.debug)

    # 仕様上、重複が発生するため除外
    result = sorted(set(result), key=result.index)
    for link in result:
        print(header + link)


# bingでのsuggest取得
def suggest(args):
    # enginecommon
    bing = SearchEngine()
    bing.set('bing')

    # proxy
    if args.proxy != '':
        bing.set_proxy(args.proxy)

    # header
    header = '[BingSuggest]: '
    if args.color == 'always':
        header = Color.CYAN + header + Color.END
    elif args.color == 'auto' and sys.stdout.isatty():
        header = Color.CYAN + header + Color.END

    # BingでのSuggestを取得
    result = bing.suggest(
        args.query,
        jap=args.jap,
        alph=args.alph,
        num=args.num
    )
    for words in result.values():
        for w in words:
            print(header + w)
