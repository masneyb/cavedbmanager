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

# To run:
#
#   cd /path/to/cavedbmanager
#   DJANGO_SETTINGS_MODULE=cavedb.settings \
#     PYTHONPATH=. \
#     python ./cavedb/scripts/generate_single_bulletin.py <bulletin id>

import sys
import django
import cavedb.generate_docs
import cavedb.utils

django.setup()

if len(sys.argv) != 2:
    print 'usage: generate_single_doc.py <bulletin ID>'
    sys.exit(1)

bulletin_id = sys.argv[1]

if bulletin_id == cavedb.utils.GLOBAL_BULLETIN_ID:
    cavedb.generate_docs.write_global_bulletin_files()
else:
    bulletins = cavedb.models.Bulletin.objects.filter(id=bulletin_id)
    if bulletins.count() == 0:
        print 'Bulletin %s not found' % (bulletin_id)
        sys.exit(1)

    bulletin = bulletins[0]

    cavedb.generate_docs.write_bulletin_files(bulletin)

cavedb.generate_docs.run_buildscript_wrapper(bulletin_id)
