#!/bin/bash -u
# SPDX-License-Identifier: Apache-2.0

sed "s%__CAVEDB_WORKER_MSG_DIR__%$CAVEDB_WORKER_MSG_DIR%g" /etc/crontab.template > /etc/crontab
exec cron -f
