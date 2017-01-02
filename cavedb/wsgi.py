# Copyright 2016 Brian Masney <masneyb@onstation.org>
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

import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'cavedb.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cavedb.settings")
sys.path.append('/usr/local/cavedbmanager/cavedb/')
sys.path.append('/usr/local/cavedbmanager/')

#pylint: disable=invalid-name
application = get_wsgi_application()
