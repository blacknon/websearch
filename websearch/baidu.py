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
def search(args, cmd=False):
    print(cmd)

    # baidu class
    baidu = SearchEngine()
    baidu.set('baidu')

    # lang/country code
    baidu.set_lang(args.lang, args.country)

    # proxy
    if args.proxy != '' and args.splash == '':
        baidu.set_proxy(args.proxy)

    # Splush
    if args.splash != '':
        baidu.SPLASH_URL = 'http://' + args.splash + '/render.html?'

        # Proxyが指定されている場合
        if args.proxy != '':
            baidu.SPLASH_URL = baidu.SPLASH_URL + 'proxy=' + args.proxy + '&'

        baidu.SPLASH_URL = baidu.SPLASH_URL + 'url='

    # Header
    header = '[BaiduSearch]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = Color.RED + header + Color.END

    # 検索タイプを設定(テキスト or 画像)
    search_type = 'text'

    # baidu検索を実行
    result = baidu.search(args.query, type=search_type,
                          maximum=args.num, debug=args.debug,
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


# baiduでのsuggest取得
def suggest(args, cmd=False):
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
        num=args.num,
        cmd=cmd
    )

    for words in result.values():
        for w in words:
            print(header + w)
