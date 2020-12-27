#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2020 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================


import sys

from .search import SearchEngine
from .common import Color


# DuckDuckGoでの検索
def search(args, cmd=False):
    # duckduckgo class
    duckduckgo = SearchEngine()

    # Splush
    if args.splash != '':
        duckduckgo.SPLASH_URL = 'http://' + args.splash + '/render.html?'

        # Proxyが指定されている場合
        if args.proxy != '':
            duckduckgo.SPLASH_URL = duckduckgo.SPLASH_URL + 'proxy=' + args.proxy + '&'

        duckduckgo.SPLASH_URL = duckduckgo.SPLASH_URL + 'url='

    # Set Engine
    duckduckgo.set('duckduckgo')

    # Proxy
    if args.proxy != '' and args.splash == '':
        duckduckgo.set_proxy(args.proxy)

    # Header
    header = '[DuckDuckGoSearch]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = Color.BLUE + header + Color.END

    # 検索タイプを設定(テキスト or 画像)
    search_type = 'text'

    # duckduckgo検索を実行
    result = duckduckgo.search(args.query, type=search_type,
                               maximum=args.num, debug=args.debug,
                               start=args.start, end=args.end,
                               cmd=cmd)

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


# duckduckgoでのsuggest取得
def suggest(args, cmd=False):
    # engine
    duckduckgo = SearchEngine()
    duckduckgo.set('duckduckgo')

    # header
    header = '[DuckDuckGoSuggest]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = Color.BLUE + header + Color.END

    # duckduckgoでのSuggestを取得
    result = duckduckgo.suggest(
        args.query,
        jap=args.jap,
        alph=args.alph,
        num=args.num,
        cmd=cmd
    )
    for words in result.values():
        for w in words:
            print(header + w)
