#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2019 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import sys

from .search import SearchEngine
from .common import Color, get_unique_list


# bingでの検索
def search(args, cmd=False):
    # engine
    bing = SearchEngine()

    # Proxy
    if args.proxy != '' and args.splash == '':
        bing.set_proxy(args.proxy)

    # Splush
    if args.splash != '':
        bing.SPLASH_URL = 'http://' + args.splash + '/render.html?'

        # Proxyが指定されている場合
        if args.proxy != '':
            bing.SPLASH_URL = bing.SPLASH_URL + 'proxy=' + args.proxy + '&'

        bing.SPLASH_URL = bing.SPLASH_URL + 'url='

    # Set Engine
    bing.set('bing')

    # lang/country code
    bing.set_lang(args.lang, args.country)

    # Header
    header = '[BingSearch]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = Color.CYAN + header + Color.END

    # 検索タイプを設定(テキスト or 画像)
    search_type = 'text'

    # Bingでの検索を実
    result = bing.search(args.query, type=search_type,
                         maximum=args.num, debug=args.debug,
                         start=args.start, end=args.end,
                         cmd=cmd)

    # 仕様上、重複が発生するため除外
    result = get_unique_list(result)

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


# bingでのsuggest取得
def suggest(args, cmd=False):
    # enginecommon
    bing = SearchEngine()
    bing.set('bing')

    # proxy
    if args.proxy != '':
        bing.set_proxy(args.proxy)

    # header
    header = '[BingSuggest]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = Color.CYAN + header + Color.END

    # BingでのSuggestを取得
    result = bing.suggest(
        args.query,
        jap=args.jap,
        alph=args.alph,
        num=args.num,
        cmd=cmd
    )
    for words in result.values():
        for w in words:
            print(header + w)
