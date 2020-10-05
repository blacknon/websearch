#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2019 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import argparse
from datetime import datetime
import threading

from . import bing, google, yahoo, baidu
from pkg_resources import get_distribution

# version (setup.pyから取得してくる)
__version__ = get_distribution('websearch').version


# searchサブコマンドでの動作
def command_search(args):
    # args.startもしくはargs.endだけ指定されている場合
    if (args.start is None and args.end is not None) or (args.start is not None and args.end is None):
        print("期間を指定する場合は--start, --endの両方を指定してください")
        return

    for st in args.search_type:
        # if all
        if st == 'all':
            thread_baidu = threading.Thread(
                target=baidu.search, args=([args]))
            thread_bing = threading.Thread(
                target=bing.search, args=([args]))
            thread_google = threading.Thread(
                target=google.search, args=([args]))
            thread_yahoo = threading.Thread(
                target=yahoo.search, args=([args]))

            thread_baidu.start()
            thread_bing.start()
            thread_google.start()
            thread_yahoo.start()
            continue

        # if baidu
        if st == 'baidu':
            thread_baidu = threading.Thread(
                target=baidu.search, args=([args]))
            thread_baidu.start()
            continue

        # if bing
        if st == 'bing':
            thread_bing = threading.Thread(
                target=bing.search, args=([args]))
            thread_bing.start()
            continue

        # if google
        if st == 'google':
            thread_google = threading.Thread(
                target=google.search, args=([args]))
            thread_google.start()
            continue

        # if yahoo
        if st == 'yahoo':
            thread_yahoo = threading.Thread(
                target=yahoo.search, args=([args]))
            thread_yahoo.start()
            continue


# suggestサブコマンドでの動作
def command_suggest(args):
    for st in args.search_type:
        # if all
        if st == 'all':
            thread_baidu = threading.Thread(
                target=baidu.suggest, args=([args]))
            thread_bing = threading.Thread(
                target=bing.suggest, args=([args]))
            thread_google = threading.Thread(
                target=google.suggest, args=([args]))
            thread_yahoo = threading.Thread(
                target=yahoo.suggest, args=([args]))

            thread_baidu.start()
            thread_bing.start()
            thread_google.start()
            thread_yahoo.start()
            continue

        # if baidu
        if st == 'baidu':
            thread_baidu = threading.Thread(
                target=baidu.suggest, args=([args]))
            thread_baidu.start()
            continue

        # if bing
        if st == 'bing':
            thread_bing = threading.Thread(
                target=bing.suggest, args=([args]))
            thread_bing.start()
            continue

        # if google
        if st == 'google':
            thread_google = threading.Thread(
                target=google.suggest, args=([args]))
            thread_google.start()
            continue

        # if yahoo
        if st == 'yahoo':
            thread_yahoo = threading.Thread(
                target=yahoo.suggest, args=([args]))
            thread_yahoo.start()
            continue


# main
def main():
    # parserの作成
    parser = argparse.ArgumentParser(
        description='各種サーチエンジンから指定したクエリの結果(url)およびSuggestを取得するスクリプト')
    subparsers = parser.add_subparsers()

    # search
    parser_search = subparsers.add_parser(
        'search', help='search mode. see `search -h`')
    parser_search.add_argument(
        'query', action='store', type=str, help='query')
    parser_search.add_argument(
        '-t', '--search_type', default=['google'],
        choices=[
            'baidu',
            'bing',
            'google',
            'yahoo',
            'all'
        ],
        nargs='+', type=str, help='検索エンジンを指定')
    parser_search.add_argument(
        '-T', '--title', action='store_true',
        help='検索結果のタイトルも出力する'
    )
    parser_search.add_argument(
        '-0', '--nullchar', action='store_true',
        help='null characterを区切り文字として使用する'
    )
    parser_search.add_argument(
        '-n', '--num', default=300, type=int, help='検索結果の取得数'
    )
    parser_search.add_argument(
        '-P', '--proxy', type=str, default='',
        help='プロキシサーバ(例:socks5://hogehoge:8080,https://fugafuga:18080)'
    )
    parser_search.add_argument(
        '-S', '--splash', type=str, default='',
        help='Splash(ヘッドレスブラウザ)を利用する場合、そのアドレスを指定。'
        '(例: localhost:8050 => http://localhost:8050/render.html?url=https://www.google.co.jp/search?hogehoge...)'
    )
    parser_search.add_argument(
        '--start', type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help='期間指定(開始)'
    )
    parser_search.add_argument(
        '--end', type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
        help='期間指定(終了)'
    )
    parser_search.add_argument(
        '--debug', action='store_true', help='debug mode')  # debug
    parser_search.add_argument(
        '--color', default='auto', choices=['auto', 'none', 'always'],
        type=str, help='color出力の切り替え')
    parser_search.set_defaults(handler=command_search)

    # suggest
    parser_suggest = subparsers.add_parser(
        'suggest', help='suggest mode. see `suggest -h`')
    parser_suggest.add_argument(
        'query', action='store', type=str, help='query')
    parser_suggest.add_argument(
        '-t', '--search_type', default=['google'],
        choices=[
            'baidu',
            'bing',
            'google',
            'yahoo',
            'all'
        ],
        nargs='+', type=str, help='検索エンジンを指定')
    parser_suggest.add_argument(
        '--jap', action='store_true', help='日本語の文字を検索キーワードに追加してサジェストを取得'
    )
    parser_suggest.add_argument(
        '--alph', action='store_true', help='アルファベット文字を検索キーワードに追加してサジェストを取得'
    )
    parser_suggest.add_argument(
        '--num', action='store_true', help='数字を検索キーワードに追加してサジェストを取得'
    )
    parser_suggest.add_argument(
        '--color', default='auto', choices=['auto', 'none', 'always'],
        type=str, help='color出力の切り替え')
    parser_suggest.set_defaults(handler=command_suggest)

    # TODO(blacknon): image検索を追加する
    # image

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
