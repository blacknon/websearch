#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2019 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import setuptools
from searchurl import __version__


if __name__ == "__main__":
    setuptools.setup(
        name='searchurl',
        version=__version__,
        install_requires=['argparse', 'bs4', 'fake_useragent'],
        packages=setuptools.find_packages(),
        py_modules=['searchurl'],
        entry_points={
            'console_scripts': [
                'searchurl = searchurl:main',
            ],
        },
    )
