#!/usr/bin/env python3

# Copyright 2017 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import django
import cavedb.utils

def do_build_bulletin(bulletin_id):
    django.setup()

    from cavedb.generate_docs import write_global_bulletin_files
    from cavedb.generate_docs import write_bulletin_files
    from cavedb.generate_docs import run_buildscript

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
