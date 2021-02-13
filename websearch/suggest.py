#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================
# Copyright(c) 2019 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

import sys

from .engine import SearchEngine
from .common import Color


def suggest(engine, args, cmd=False):
    # engine
    se = SearchEngine()
    se.set(engine)

    # header
    header = '[' + se.ENGINE + 'Suggest]: '
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        header = se.COLOR + header + Color.END

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
