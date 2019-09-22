#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2019 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import os
import platform

import setuptools
from searchurl import __version__


# 補完ファイルインストール用関数
def get_data_files():

    def get_completion_install_location(shell):
        uname = platform.uname()[0]
        is_root = (os.geteuid() == 0)
        prefix = ''
        if is_root:
            # this is system install
            if uname == 'Linux' and shell == 'bash':
                prefix = '/'
            elif uname == 'Linux' and shell == 'zsh':
                prefix = '/usr/local'
            elif uname == 'Darwin' and shell == 'bash':
                prefix = '/'
            elif uname == 'Darwin' and shell == 'zsh':
                prefix = '/usr'
        if shell == 'bash':
            location = os.path.join(prefix, 'etc/bash_completion.d')
        elif shell == 'zsh':
            location = os.path.join(prefix, 'share/zsh/site-functions')
        else:
            raise ValueError('unsupported shell: {0}'.format(shell))
        return location

    loc = {'bash': get_completion_install_location(shell='bash'),
           'zsh': get_completion_install_location(shell='zsh')}
    files = dict(bash=['completion/searchurl-completion.bash'],
                 zsh=['completion/searchurl-completion.bash',
                      'completion/_searchurl'])
    data_files = []
    data_files.append((loc['bash'], files['bash']))
    data_files.append((loc['zsh'], files['zsh']))
    return data_files


if __name__ == "__main__":
    setuptools.setup(
        name='searchurl',
        version=__version__,
        install_requires=[
            'argparse',
            'bs4',
            'fake_useragent',
            'lxml'
        ],
        url='https://github.com/blacknon/searchurl',
        packages=setuptools.find_packages(),
        py_modules=['searchurl'],
        entry_points={
            'console_scripts': [
                'searchurl = searchurl:main',
            ],
        },
        data_files=get_data_files(),
    )
