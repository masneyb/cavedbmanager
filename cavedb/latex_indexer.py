# Copyright 2007-2016 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

# FIXME - do the following things:
# - write unit tests
# - ensure nested replacements are not performed

import re

class LatexIndexer(object):
    def __init__(self):
        self.indexed_terms = [], {}


    def add_to_index(self, search_term):
        all_index_terms = search_term.split(':')
        if len(all_index_terms) == 1:
            self.indexed_terms[0].append(search_term)
            self.indexed_terms[1][search_term] = r'\index{%s}%s' % (search_term, search_term)
        else:
            replacement = ''
            for index_term in all_index_terms[1:]:
                replacement = r'%s\index{%s}' % (replacement, index_term)

            self.indexed_terms[0].append(all_index_terms[0])
            self.indexed_terms[1][all_index_terms[0]] = '%s%s' % \
                (replacement, all_index_terms[0])


    def sort_index_terms(self):
        self.indexed_terms[0].sort(key=lambda term: len(term), reverse=True)


    def clean_index(self, inputstr):
        # FIXME - ugly hack for Tucker County
        inputstr = inputstr.replace(r"\caveindex{\caveindex{Great Cave} of \caveindex{Dry Fork} of Cheat River}", \
                                    r"\caveindex{Great Cave of Dry Fork of Cheat River}")
        inputstr = inputstr.replace(r"\caveindex{\caveindex{Great Cave} of \caveindex{Dry Fork} of \caveindex{Cheat River}}", \
                                    r"\caveindex{Great Cave of Dry Fork of Cheat River}")

        flags = re.MULTILINE | re.DOTALL | re.VERBOSE
        result = re.compile(r'(.*?)(\\caveindex{)(.*?)}(.*)', flags).match(inputstr)
        if not result:
            return inputstr
        elif re.compile(r'^\\caveindex{.*', flags).match(result.group(3)):
            value = re.sub(r'^\\caveindex{', '', result.group(3))
            return '%s%s%s%s' % (result.group(1), result.group(2), value, \
                                 self.clean_index(result.group(4)))
        elif not re.compile(r'^.*\\caveindex.*$', flags).match(result.group(3)):
            if re.compile(r'^.*\\caveindex.*$', flags).match(result.group(4)):
                return '%s%s%s}%s' % (result.group(1), result.group(2), result.group(3), \
                                      self.clean_index(result.group(4)))
            else:
                return inputstr
        else:
            value = re.sub(r'^(.*?)\s\\caveindex{(.*)', r'\1 \2', result.group(3))
            return '%s%s' % (result.group(1),
                             self.clean_index('%s%s%s' % (result.group(2), value, result.group(4))))


    def finalize_index(self, inputstr):
        flags = re.MULTILINE | re.DOTALL | re.VERBOSE
        result = re.compile(r'(.*?)\\caveindex{(.*?)}(.*)', flags).match(inputstr)
        if not result:
            return inputstr

        return '%s%s%s' % (result.group(1), self.indexed_terms[1][result.group(2)], \
                           self.finalize_index(result.group(3)))


    def generate_index(self, inputstr):
        # Add terms to the index
        for term in self.indexed_terms[0]:
            # This appears to be quicker than doing a single regular expression
            inputstr = inputstr.replace('%s ' % (term), r'\caveindex{%s} ' % (term))
            inputstr = inputstr.replace('%s.' % (term), r'\caveindex{%s}.' % (term))
            inputstr = inputstr.replace('%s,' % (term), r'\caveindex{%s},' % (term))
            inputstr = inputstr.replace('%s:' % (term), r'\caveindex{%s}:' % (term))
            inputstr = inputstr.replace('%s)' % (term), r'\caveindex{%s})' % (term))
            inputstr = inputstr.replace('%s\'' % (term), r'\caveindex{%s}\'' % (term))

        return self.finalize_index(self.clean_index(inputstr))

