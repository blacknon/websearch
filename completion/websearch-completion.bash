#!bash
# =======================================================
# Copyright(c) 2019 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

_websearch()
{
  local cur
  local cmd

  cur=${COMP_WORDS[$COMP_CWORD]}
  cmd=( ${COMP_WORDS[@]} )

  if [[ "$cur" == -* ]]; then
    COMPREPLY=( $( compgen -W "-h --help" -- $cur ) )
    return 0
  fi
}

complete -F _websearch -o default websearch
