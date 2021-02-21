#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

# TODO: 以下のようなre-captchaへの対応を追加する
#       - エラーを返すようにする(識別処理の追加)
#       - 操作を途中で停止してCookieを受け付ける処理を挟めるようにすることで、やり直しでのリクエストを受け付けるようにする
#       - anticaptchaを入れて対策する(Seleniumが必要かも？)。APIの指定をオプション等でできるようにしたほうがいいかも？？
#       - 参考
#         - https://github.com/ad-m/python-anticaptcha
#         - https://github.com/chr0x6eos/ReCaptchaBypass
#         - https://qiita.com/derodero24/items/7d36f4617a40fbb36b11

# TODO: Seleniumへの対応が必要(オプションの追加)
#       - Splashとの排他が必要？？(どちらかを優先でも可)


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
