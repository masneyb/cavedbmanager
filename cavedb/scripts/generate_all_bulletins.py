#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import django

django.setup()

# pylint: disable=wrong-import-position
import cavedb.utils
import cavedb.views

for bulletin in cavedb.models.Bulletin.objects.all():
    cavedb.views.queue_bulletin_generation(bulletin.id)

cavedb.views.queue_bulletin_generation(cavedb.utils.GLOBAL_BULLETIN_ID)
