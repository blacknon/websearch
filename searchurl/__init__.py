#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2019 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import argparse
import threading

from . import search, bing, google, yahoo


# version
__version__ = '0.0.1'


# searchサブコマンドでの動作
def command_search(args):
    # if all
    if args.search_type == 'all':
        thread_bind = threading.Thread(
            target=bing.search, args=([args]))
        thread_google = threading.Thread(
            target=google.search, args=([args]))
        thread_yahoo = threading.Thread(
            target=yahoo.search, args=([args]))

        thread_bind.start()
        thread_google.start()
        thread_yahoo.start()
        return

    # if bing
    if args.search_type == 'bing':
        bing.search(args)
        return

    # if google
    if args.search_type == 'google':
        google.search(args)
        return

    # if yahoo
    if args.search_type == 'yahoo':
        yahoo.search(args)
        return


# suggestサブコマンドでの動作
def command_suggest(args):
    # if all
    if args.search_type == 'all':
        thread_bind = threading.Thread(
            target=bing.suggest, args=([args]))
        thread_google = threading.Thread(
            target=google.suggest, args=([args]))
        thread_yahoo = threading.Thread(
            target=yahoo.suggest, args=([args]))

        thread_bind.start()
        thread_google.start()
        thread_yahoo.start()
        return

    # if bing
    if args.search_type == 'bing':
        bing.suggest(args)
        return

    # if google
    if args.search_type == 'google':
        google.suggest(args)
        return

    # if yahoo
    if args.search_type == 'yahoo':
        yahoo.suggest(args)
        return


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
    parser_search.add_argument('-t', '--search_type', default='google',
                               choices=[
                                   'bing',
                                   'google',
                                   'yahoo',
                                   'all'
                               ],
                               type=str, help='検索エンジンを指定')
    parser_search.add_argument(
        '-i', '--image', action='store_true', help='画像検索を行う(現在はGoogleのみ利用可能.Splash経由だとエラーになるので注意)'
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
        '(例: localhost:8050 => '
        'http://localhost:8050/render.html?url=https://www.google.co.jp/search?hogehoge...)'
    )
    parser_search.add_argument(
        '--debug', action='store_true', help='debug mode')  # debug
    parser_search.add_argument(
        '--color', default='auto', choices=['auto', 'none', 'always'], type=str, help='color出力の切り替え')
    parser_search.set_defaults(handler=command_search)

    # suggest
    parser_suggest = subparsers.add_parser(
        'suggest', help='suggest mode. see `suggest -h`')
    parser_suggest.add_argument(
        'query', action='store', type=str, help='query')
    parser_suggest.add_argument('-t', '--search_type', default='google',
                                choices=[
                                    'bing',
                                    'google',
                                    'yahoo',
                                    'all'
                                ],
                                type=str, help='検索エンジンを指定')
    parser_suggest.add_argument(
        '-P', '--proxy', type=str, help='プロキシサーバ(例:socks5://hogehoge:8080,https://fugafuga:18080)')
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
        '--color', default='auto', choices=['auto', 'none', 'always'], type=str, help='color出力の切り替え')
    parser_suggest.set_defaults(handler=command_suggest)

    # --version(-v)オプションのparser定義
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__)
    )

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        # 未知のサブコマンドの場合はヘルプを表示
        parser.print_help()


if __name__ == '__main__':
    main()
