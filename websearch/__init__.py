#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

# TODO: mapを別ファイルに移動する
# TODO: subcommand用functionを別ファイルに移動する

import argparse
import copy
import threading

from datetime import datetime
from pkg_resources import get_distribution

from .subcommands import search, suggest

# version (setup.pyから取得してくる)
__version__ = get_distribution('websearch').version


# searchサブコマンドでの動作
def command_search(args):
    # args.startもしくはargs.endだけ指定されている場合
    if ((args.start is None and args.end is not None) or (args.start is not None and args.end is None)):
        print("期間を指定する場合は--start, --endの両方を指定してください")
        return

    tasks = []
    for st in args.search_type:
        # if all
        if st == 'all':
            engines = ['baidu', 'bing', 'duckduckgo', 'google', 'yahoo']

            for engine in engines:
                task = threading.Thread(
                    target=search, args=(engine, args, True))
                tasks.append(task)

            continue

        # if in searchengine
        if st in {'baidu', 'bing', 'duckduckgo', 'google', 'yahoo'}:
            task = threading.Thread(
                target=search, args=(st, args, True))
            tasks.append(task)

            continue

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()


# suggestサブコマンドでの動作
def command_suggest(args):
    tasks = []
    for st in args.search_type:
        # if all
        if st == 'all':
            engines = ['baidu', 'bing', 'duckduckgo', 'google', 'yahoo']

            for engine in engines:
                task = threading.Thread(
                    target=suggest, args=(engine, args, True))
                tasks.append(task)

            continue

        # if in searchengine
        if st in {'baidu', 'bing', 'duckduckgo', 'google', 'yahoo'}:
            task = threading.Thread(
                target=suggest, args=(st, args, True))
            tasks.append(task)

            continue

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()


# main
def main():
    # parserの作成
    parser = argparse.ArgumentParser(
        description='各種サーチエンジンから指定したクエリの結果(url)およびSuggestを取得するスクリプト')
    subparsers = parser.add_subparsers()

    # サブコマンド共通の引数
    common_args_map = [
        {
            "args": ["query"],
            "action": "store",
            "type": str,
            "help": "検索文字列(クエリ)",
        },
        {
            "args": ["-t", "--search_type"],
            "default": "google",
            "choices": ["baidu", "bing", "duckduckgo", "google", "yahoo", "all"],
            "nargs": "+",
            "type": str,
            "help": "使用する検索エンジンを指定",
        },
        {
            "args": ["-l", "--lang"],
            "default": "ja",
            "choices": ["JP", "US"],
            "type": str,
            "help": "言語を指定",
        },
        {
            "args": ["-c", "--country"],
            "default": "JP",
            "choices": ["JP", "US"],
            "type": str,
            "help": "言語を指定",
        },
        {
            "args": ["-P", "--proxy"],
            "default": "",
            "type": str,
            "help": "プロキシサーバーを指定(例:socks5://hogehoge:8080, https://fugafuga:18080)",
        },
        {
            "args": ["-s", "--selenium"],
            "action": "store_true",
            "help": "Selenium(headless browser)を使用する(排他: Splashより優先)",
        },
        {
            "args": ["-S", "--splash"],
            "action": "store_true",
            "help": "Splash(headless browser)を使用する(排他: Seleniumの方が優先)",
        },
        {
            "args": ["-e", "--browser-endpoint"],
            "default": "",
            "type": str,
            "help": "Selenium/Splash等のヘッドレスブラウザのエンドポイントを指定(例: localhost:8050)",
        },
        {
            "args": ["--color"],
            "default": "auto",
            "choices": ["auto", "none", "always"],
            "type": str,
            "help": "color出力の切り替え"
        },
    ]

    # サブコマンド `search` の引数
    search_args_map = [
        {
            "args": ["-T", "--title"],
            "action": "store_true",
            "help": "検索結果のタイトルをセットで出力する",
        },
        {
            "args": ["-0", "--nullchar"],
            "action": "store_true",
            "help": "null characterを区切り文字として使用する",
        },
        {
            "args": ["-n", "--num"],
            "default": 300,
            "type": int,
            "help": "検索結果の取得数を指定する",
        },
        {
            "args": ["--start"],
            "type": lambda s: datetime.strptime(s, '%Y-%m-%d'),
            "help": "期間指定(開始)",
        },
        {
            "args": ["--end"],
            "type": lambda s: datetime.strptime(s, '%Y-%m-%d'),
            "help": "期間指定(終了)",
        },
        {
            "args": ["--debug"],
            "action": "store_true",
            "help": "debugモードを有効にする",
        },
    ]
    search_args_map.extend(copy.deepcopy(common_args_map))

    # サブコマンド `image` の引数

    # サブコマンド `suggest` の引数
    suggest_args_map = [
        {
            "args": ["--jap"],
            "action": "store_true",
            "help": "日本語の文字を検索キーワードに追加してサジェストを取得"
        },
        {
            "args": ["--alph"],
            "action": "store_true",
            "help": "アルファベット文字を検索キーワードに追加してサジェストを取得"
        },
        {
            "args": ["--num"],
            "action": "store_true",
            "help": "数字を検索キーワードに追加してサジェストを取得"
        },
    ]
    suggest_args_map.extend(copy.deepcopy(common_args_map))

    # search
    # ----------
    parser_search = subparsers.add_parser(
        'search',
        help='search mode. see `search -h`'
    )

    # add_argument
    for element in search_args_map:
        args = element['args']
        element.pop('args')
        parser_search.add_argument(*args, **element)

    # set parser_search
    parser_search.set_defaults(handler=command_search)

    # image
    # ----------

    # TODO(blacknon): image検索をサブコマンドとして追加する
    # parser_image

    # suggest
    # ----------
    parser_suggest = subparsers.add_parser(
        'suggest',
        help='suggest mode. see `suggest -h`'
    )

    # add_argument
    for element in suggest_args_map:
        args = element['args']
        element.pop('args')
        parser_suggest.add_argument(*args, **element)

    parser_suggest.set_defaults(handler=command_suggest)

    # --version(-v)オプションのparser定義
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s version:{version}'.format(version=__version__)
    )

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        # 未知のサブコマンドの場合はヘルプを表示
        parser.print_help()


if __name__ == '__main__':
    main()
