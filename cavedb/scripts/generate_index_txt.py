#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import os
import django
from django.conf import settings

django.setup()

# pylint: disable=wrong-import-position
import cavedb.models

def get_directory(name):
    directory = os.path.join(settings.MEDIA_ROOT, name)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    return directory

def generate_bulletins():
    attachment_filename = os.path.join(get_directory('bulletin_attachments'), 'index.txt')
    bulletin_filename = os.path.join(get_directory('bulletins'), 'index.txt')
    with open(attachment_filename, 'w', encoding='utf-8') as attachment_index, \
         open(bulletin_filename, 'w', encoding='utf-8') as bulletin_index:
        attachment_index.write('ID\tBulletin Name\r\n')
        bulletin_index.write('ID\tBulletin Name\r\n')

        for bulletin in cavedb.models.Bulletin.objects.all():
            attachment_index.write('%d\t%s\r\n' % (bulletin.id, bulletin.bulletin_name))
            bulletin_index.write('bulletin_%d\t%s\r\n' % (bulletin.id, bulletin.bulletin_name))

        bulletin_index.write('bulletin_global\tGenerated artifacts for the entire state\r\n')

def generate_features():
    filename = os.path.join(get_directory('feature_attachments'), 'index.txt')
    with open(filename, 'w', encoding='utf-8') as output:
        output.write('ID\tBulletin\tName\r\n')

        for feature in cavedb.models.Feature.objects.all():
            output.write('%d\t%s\t%s\r\n' % (feature.id,
                                             feature.bulletin_region.bulletin.short_name,
                                             feature.name))

def generate_statewide_docs():
    filename = os.path.join(get_directory('statewide_docs'), 'index.txt')
    with open(filename, 'w', encoding='utf-8') as output:
        output.write('ID\tDescription\r\n')

        for doc_type in cavedb.models.StatewideDocType.objects.all():
            output.write('%d\t%s\r\n' % (doc_type.id, doc_type.description))

def generate_index_txt():
    generate_bulletins()
    generate_features()
    generate_statewide_docs()

if __name__ == '__main__':
    generate_index_txt()
