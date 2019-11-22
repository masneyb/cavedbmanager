#!/usr/bin/env python3

# Copyright 2019 Brian Masney <masneyb@onstation.org>
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

import os
import django
from django.conf import settings

django.setup()

# pylint: disable=wrong-import-position
import cavedb.models

def generate_bulletins():
    attachment_filename = os.path.join(settings.MEDIA_ROOT, 'bulletin_attachments', 'index.txt')
    bulletin_filename = os.path.join(settings.MEDIA_ROOT, 'bulletins', 'index.txt')
    with open(attachment_filename, 'w') as attachment_index, \
         open(bulletin_filename, 'w') as bulletin_index:
        attachment_index.write('ID\tBulletin Name\r\n')
        bulletin_index.write('ID\tBulletin Name\r\n')

        for bulletin in cavedb.models.Bulletin.objects.all():
            attachment_index.write('%d\t%s\r\n' % (bulletin.id, bulletin.bulletin_name))
            bulletin_index.write('bulletin_%d\t%s\r\n' % (bulletin.id, bulletin.bulletin_name))

        bulletin_index.write('bulletin_global\tGenerated artifacts for the entire state\r\n')

def generate_features():
    filename = os.path.join(settings.MEDIA_ROOT, 'feature_attachments', 'index.txt')
    with open(filename, 'w') as output:
        output.write('ID\tBulletin\tName\r\n')

        for feature in cavedb.models.Feature.objects.all():
            output.write('%d\t%s\t%s\r\n' % (feature.id,
                                             feature.bulletin_region.bulletin.short_name,
                                             feature.name))

def generate_statewide_docs():
    filename = os.path.join(settings.MEDIA_ROOT, 'statewide_docs', 'index.txt')
    with open(filename, 'w') as output:
        output.write('ID\tDescription\r\n')

        for doc_type in cavedb.models.StatewideDocType.objects.all():
            output.write('%d\t%s\r\n' % (doc_type.id, doc_type.description))

def generate_index_txt():
    generate_bulletins()
    generate_features()
    generate_statewide_docs()

if __name__ == '__main__':
    generate_index_txt()
