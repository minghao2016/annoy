# Copyright (c) 2013 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import unittest
import random
import os
from annoy import AnnoyIndex
import urllib
import gzip

class AccuracyTest(unittest.TestCase):
    def _get_index(self, f, distance):
        input = 'test/glove.twitter.27B.%dd.txt.gz' % f
        output = 'test/glove.%d.%s.annoy' % (f, distance)
        
        if not os.path.exists(output):
            if not os.path.exists(input):
                # Download GloVe pretrained vectors: http://nlp.stanford.edu/projects/glove/
                url = 'http://www-nlp.stanford.edu/data/glove.twitter.27B.%dd.txt.gz' % f
                print 'downloading', url, '->', input
                urllib.urlretrieve(url, input)

            print 'building index', distance, f
            annoy = AnnoyIndex(f, distance)
            for i, line in enumerate(gzip.open(input, 'rb')):
                v = map(float, line.strip().split()[1:])
                annoy.add_item(i, v);
                
            annoy.build(10)
            annoy.save(output)

        annoy = AnnoyIndex(f, distance)
        annoy.load(output)
        return annoy

    def _test_index(self, f, distance, exp_accuracy):
        annoy = self._get_index(f, distance)

        n, k = 0, 0

        for i in xrange(10000):
            js_fast = annoy.get_nns_by_item(i, 11)[1:11]
            js_slow = annoy.get_nns_by_item(i, 1001)[1:11]

            n += 10
            k += len(set(js_fast).intersection(js_slow))

        accuracy = 100.0 * k / n
        print '%20s %4d accuracy: %5.2f%%' % (distance, f, accuracy)

        self.assertTrue(accuracy > exp_accuracy - 1.0) # should be within 1%

    def test_angular_25(self):
        self._test_index(25, 'angular', 46.80)

    def test_euclidean_25(self):
        self._test_index(25, 'euclidean', 47.34)

    def test_angular_50(self):
        self._test_index(50, 'angular', 31.00)

    def test_euclidean_50(self):
        self._test_index(50, 'euclidean', 33.04)

    def test_angular_100(self):
        self._test_index(100, 'angular', 24.50)

    def test_euclidean_100(self):
        self._test_index(100, 'euclidean', 25.10)

    def test_angular_200(self):
        self._test_index(200, 'angular', 15.18)

    def test_euclidean_200(self):
        self._test_index(200, 'euclidean', 17.99)        
