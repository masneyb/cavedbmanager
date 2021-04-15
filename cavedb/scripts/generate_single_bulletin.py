#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import sys
import django

django.setup()

# pylint: disable=wrong-import-position
import cavedb.utils

from cavedb.generate_docs import write_global_bulletin_files
from cavedb.generate_docs import write_bulletin_files
from cavedb.generate_docs import run_buildscript

def do_build_bulletin(bulletin_id):
    if bulletin_id == cavedb.utils.GLOBAL_BULLETIN_ID:
        write_global_bulletin_files()
    else:
        bulletin = cavedb.models.Bulletin.objects.get(pk=bulletin_id)
        if bulletin is None:
            print('Bulletin %s not found' % (bulletin_id))
            sys.exit(1)

        write_bulletin_files(bulletin)

    run_buildscript(bulletin_id)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: generate_single_doc.py <bulletin ID>')
        sys.exit(1)

    do_build_bulletin(sys.argv[1])
