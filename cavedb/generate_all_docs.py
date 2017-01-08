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

# You can have systemd trigger rebuilds all all bulletins on a daily basis
# with this service and timer file:
#
# build-all-bulletins.service:
#
#   [Unit]
#   Description=Build all bulletins
#
#   [Service]
#   User=www-data
#   Type=simple
#   WorkingDirectory=/usr/local/cavedbmanager
#   ExecStart=/usr/bin/python ./cavedb/generate_all_docs.py
#   Environment="DJANGO_SETTINGS_MODULE=cavedb.settings"
#   Environment="PYTHONPATH=."
#
# build-all-bulletins.timer:
#
#   [Unit]
#   Description=Build all bulletins
#
#   [Timer]
#   OnCalendar=daily
#
#   [Install]
#   WantedBy=multi-user.target

import django
import cavedb.generate_docs
import cavedb.utils

django.setup()

for bulletin in cavedb.models.Bulletin.objects.all():
    print 'Generating bulletin %s (%s)\n' % (bulletin.bulletin_name, bulletin.id)
    cavedb.generate_docs.write_bulletin_files(bulletin)

print 'Generating global bulletin\n'
cavedb.generate_docs.write_global_bulletin_files()
