# SPDX-License-Identifier: Apache-2.0

from django.conf import settings

def msg_dir(message):
    filename = '%s/%s' % (settings.CAVEDB_WORKER_MSG_DIR, message)
    with open(filename, 'w', encoding='utf-8') as output:
        output.write('')
