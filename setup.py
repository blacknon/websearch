#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2021 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import os
import platform

import setuptools


# 補完ファイルインストール用関数
def get_data_files():

    # 補完ファイルのインストール先を取得する関数
    def get_completefile_install_location(shell):
        # pathのprefixを定義
        prefix = ''

        # osの種類を取得
        uname = platform.uname()[0]

        # 実行ユーザがrootかどうかでprefixを変更
        if os.geteuid() == 0:
            ''' システムインストール時の挙動 '''
            if uname == 'Linux' and shell == 'bash':
                prefix = '/'
            elif uname == 'Linux' and shell == 'zsh':
                prefix = '/usr/local'
            elif uname == 'Darwin' and shell == 'bash':
                prefix = '/'
            elif uname == 'Darwin' and shell == 'zsh':
                prefix = '/usr'

        # shellの種類に応じてインストール先のlocationを変更
        if shell == 'bash':
            location = os.path.join(prefix, 'etc/bash_completion.d')
        elif shell == 'zsh':
            location = os.path.join(prefix, 'share/zsh/site-functions')
        else:
            raise ValueError('unsupported shell: {0}'.format(shell))

        # locationを返す
        return location

    # locationをdict形式で取得する
    loc = {
        'bash': get_completefile_install_location('bash'),
        'zsh': get_completefile_install_location('zsh')
    }

    # 対象となるファイルをdict形式で指定
    files = dict(
        bash=['completion/websearch-completion.bash'],
        zsh=[
            'completion/websearch-completion.bash',
            'completion/_websearch'
        ]
    )

    # data_files形式でreturn
    data_files = []
    data_files.append((loc['bash'], files['bash']))
    data_files.append((loc['zsh'], files['zsh']))
    return data_files


if __name__ == "__main__":
    setuptools.setup(
        name='websearch',
        version='0.1.9',
        install_requires=[
            'argparse',
            'bs4',
            'fake_useragent',
            'lxml',
            'requests'
        ],
        url='https://github.com/blacknon/websearch',
        packages=setuptools.find_packages(),
        py_modules=['websearch'],
        entry_points={
            'console_scripts': [
                'websearch = websearch:main',
            ],
        },
        data_files=get_data_files(),
    )
