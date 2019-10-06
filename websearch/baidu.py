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


# baiduでの検索
def search(args):
    # baidu class
    baidu = SearchEngine()
    baidu.set('baidu')

    # proxy
    if args.proxy != '':
        baidu.set_proxy(args.proxy)

    # Splush
    # TODO(blacknon): Proxyへの対応
    if args.splash != '':
        baidu.SPLASH_URL = 'http://' + args.splash + '/render.html?url='

    # Header
    header = '[BaiduSearch]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = Color.RED + header + Color.END

    # 検索タイプを設定(テキスト or 画像)
    search_type = 'text'
    if args.image:
        search_type = 'image'

    # baidu検索を実行
    result = baidu.search(args.query, type=search_type,
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
        # titleの色指定
        title = d['title']
        if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
            title = Color.GRAY + title + ": " + Color.END

        link = d['link']
        if args.title:
            print(header + sep + title + sep + link)
        else:
            print(header + sep + link)


# baiduでのsuggest取得
def suggest(args):
    # engine
    baidu = SearchEngine()
    baidu.set('baidu')

    # header
    header = '[BaiduSuggest]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = Color.RED + header + Color.END

    # baiduでのSuggestを取得
    result = baidu.suggest(
        args.query,
        jap=args.jap,
        alph=args.alph,
        num=args.num
    )

    for words in result.values():
        for w in words:
            print(header + w)