# Copyright 2017 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# To run from the command line:
#
#   cd /path/to/cavedbmanager
#   DJANGO_SETTINGS_MODULE=cavedb.settings \
#     PYTHONPATH=. python \
#     ./cavedb/scripts/generate_all_bulletins.py

import django
import cavedb.generate_docs
import cavedb.utils

django.setup()

for bulletin in cavedb.models.Bulletin.objects.all():
    print 'Generating bulletin %s (%s)' % (bulletin.bulletin_name, bulletin.id)
    cavedb.generate_docs.write_bulletin_files(bulletin)
    cavedb.generate_docs.run_buildscript(bulletin.id)

print 'Generating global bulletin'
cavedb.generate_docs.write_global_bulletin_files()
cavedb.generate_docs.run_buildscript(cavedb.utils.GLOBAL_BULLETIN_ID)
