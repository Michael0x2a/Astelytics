#!/usr/bin/env python

import collections
import uuid

import requests

DB_URL = r"http://astelytics.nodejitsu.com"


class Survey(object):
    def __init__(self, survey_id):
        assert(isinstance(survey_id, basestring))
        
        response = requests.post(DB_URL + r"/survey/single", data={"survey_id": survey_id})
        self.survey = response.json()
        
        self.survey_id = survey_id
        self.name = self.survey[u'name']
        self.topic = self.survey[u'topic']
        self.users = self.survey[u'user']
        self.questions = [Question(q[u'question'], q[u'answers'], q[u'type']) for q in self.survey[u'questions']]
        
    def json(self):
        return self.survey
        
class Question(object):
    def __init__(self, question, answers, type):
        self.question = question
        self.unique_id = 'id-' + str(uuid.uuid5(uuid.NAMESPACE_DNS, bytes(question)))
        self.answers = answers
        self.type = type
        
    def json(self):
        return {u'question': self.question, u'answers': self.answers, 
            u'type': self.type, u'unique_id': self.unique_id}
        
class ResultsView(object):
    def __init__(self, survey):
        self.survey = survey
        self.questions = [self._custom_questions(q) for q in self.survey.questions]
        
    def _custom_questions(self, question):
        return {
            u'question': question.question,
            u'type': question.type,
            u'unique_id': question.unique_id,
            u'answers': self._format_answers_by_type(question.type, question.answers)
        }
        
    def json(self):
        return {u'results': self.questions}
        
    def find_question(self, unique_id):
        return [result for result in self.questions if result['unique_id'] == unique_id][0]
        
    def _format_answers_by_type(self, type, answers):
        clean = [answer[1] for answer in answers.items()]
        if type == u'single selection':
            return dict(collections.Counter(clean))
        else:
            return clean
        
        
        
        