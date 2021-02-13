#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import sys

from .engine import SearchEngine
from .common import Color


# 検索
def run(engine, args, cmd=False):
    # start search engine class
    se = SearchEngine()

    # proxy
    if args.proxy != '' and args.splash == '':
        se.set_proxy(args.proxy)

    # Splush
    if args.splash != '':
        se.SPLASH_URL = 'http://' + args.splash + '/render.html?'

        # Proxyが指定されている場合
        if args.proxy != '':
            se.SPLASH_URL = se.SPLASH_URL + 'proxy=' + args.proxy + '&'

        se.SPLASH_URL = se.SPLASH_URL + 'url='

    # Set Engine
    se.set(engine)

    # lang/country code
    se.set_lang(args.lang, args.country)

    # Header
    header = '[' + se.ENGINE + 'Search]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = se.COLOR + header + Color.END

    # 検索タイプを設定(テキスト or 画像)
    search_type = 'text'

    # 検索を実行
    result = se.search(
        args.query, type=search_type,
        maximum=args.num, debug=args.debug,
        cmd=cmd
    )

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
