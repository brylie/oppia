# coding: utf-8
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Jeremy Emerson'

import feconf
import oppia.apps.classifier.models as cl_models
import oppia.apps.widget.models as widget_models
import test_utils

from google.appengine.ext import db


class AnswerHandlerUnitTests(test_utils.AppEngineTestBase):
    """Test AnswerHandler models."""

    def setUp(self):
        """Loads the default classifiers."""
        super(AnswerHandlerUnitTests, self).setUp()
        cl_models.Classifier.load_default_classifiers()

    def test_rules_property(self):
        """Test that answer_handler.rules behaves as expected."""
        answer_handler = widget_models.AnswerHandler()
        answer_handler.put()
        self.assertEqual(answer_handler.name, 'submit')
        self.assertEqual(answer_handler.rules, [])

        answer_handler.classifier = 'MultipleChoiceClassifier'
        answer_handler.put()
        self.assertEqual(len(answer_handler.rules), 1)

    def test_fake_classifier_is_not_accepted(self):
        """Test validation of answer_handler.classifier."""
        answer_handler = widget_models.AnswerHandler()
        with self.assertRaises(db.BadValueError):
            answer_handler.classifier = 'FakeClassifier'

        answer_handler = widget_models.AnswerHandler(
            classifier='MultipleChoiceClassifier')
        answer_handler.put()


class WidgetUnitTests(test_utils.AppEngineTestBase):
    """Test widget models."""

    def test_parameterized_widget(self):
        """Test that parameterized widgets are correctly handled."""
        cl_models.Classifier.load_default_classifiers()

        MUSIC_STAFF_ID = 'MusicStaff'

        widget = widget_models.Registry.get_widget_by_id(
            feconf.INTERACTIVE_PREFIX, MUSIC_STAFF_ID)
        self.assertEqual(widget.id, MUSIC_STAFF_ID)
        self.assertEqual(widget.name, 'Music staff')

        code = widget.get_raw_code()
        self.assertIn('GLOBALS.noteToGuess = JSON.parse(\'\\"', code)

        code = widget.get_raw_code({'noteToGuess': 'abc'})
        self.assertIn('GLOBALS.noteToGuess = JSON.parse(\'abc\');', code)

        parameterized_widget_dict = widget.get_with_params(
            {'noteToGuess': 'abc'}
        )
        self.assertItemsEqual(parameterized_widget_dict.keys(), [
            'id', 'name', 'category', 'description',
            'params', 'handlers', 'raw'])
        self.assertEqual(parameterized_widget_dict['id'], MUSIC_STAFF_ID)
        self.assertIn('GLOBALS.noteToGuess = JSON.parse(\'abc\');',
                      parameterized_widget_dict['raw'])
        self.assertEqual(parameterized_widget_dict['params'],
                         {'noteToGuess': 'abc'})