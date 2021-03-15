#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

# TODO: 共通系の処理に渡すように加工


import sys

from .engine import SearchEngine
from .common import Color


# 検索
def search(engine, args, cmd=False):
    # start search engine class
    se = SearchEngine()

    # Set Engine
    se.set(engine)

    # proxy
    if args.proxy != '':
        se.set_proxy(args.proxy)

    # Splush
    if args.splash != '':
        se.set_splash_url(args.splash)

    # useragent
    se.set_useragent()

    # lang/country code
    se.set_lang(args.lang, args.country)

    # Header
    header = '[' + se.ENGINE.NAME + 'Search]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = se.ENGINE.COLOR + header + Color.END

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


# 画像検索
# def image(engine, args, cmd=False):

# サジェスト
def suggest(engine, args, cmd=False):
    # engine
    se = SearchEngine()
    se.set(engine)

    # header
    header = '[' + se.ENGINE.NAME + 'Suggest]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = se.ENGINE.COLOR + header + Color.END

    # useragent
    se.set_useragent()

    # proxy
    if args.proxy != '':
        se.set_proxy(args.proxy)

    # Splush
    if args.splash != '':
        se.set_splash_url(args.splash)

    # lang/country code
    se.set_lang(args.lang, args.country)

    # Suggestを取得
    result = se.suggest(
        args.query,
        jap=args.jap,
        alph=args.alph,
        num=args.num,
        cmd=cmd
    )

    for words in result.values():
        for w in words:
            print(header + w)
