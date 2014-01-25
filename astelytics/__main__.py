#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import functools
import copy
import re

import flask
from flask.ext.classy import FlaskView, route
from flask_sockets import Sockets


app = flask.Flask(__name__, static_folder='static')
app.secret_key = ',*\xee\xd6tJ1Ja\xc8D\x9d!-\xa2k\xb6K\x9e\xb8\xff\xd7z\xc3'
sockets = Sockets(app)

# This is our "fake" database.
db = {}



def support_jsonp(json):
    '''Optionally enables support for jsonp, if requested.'''
    callback = flask.request.args.get('callback', False)
    if callback:
        content = str(callback) + '(' + json + ')'
        return flask.current_app.response_class(content, mimetype='application/json')
    else:
        return json
        
def rank_words(words, n):
    boring = {'the', 'of', 'a', 'an', 'or', 'some', 'will', 'and', 'for', 
        'should', 'would', 'did', 'does', 'do', 'but', 'yet', 'nor', 'it', 'was', ''}
    clean = re.sub('[.,-;:]', ' ', words.lower())
    clean = re.sub('[^a-z0-9 ]', '', clean)
    clean = [a for a in clean.split(' ') if a not in boring] 
    # I can't convert 'clean' to a set, since then it would squash duplicate 
    # occurances of a word.
    return collections.Counter(clean).most_common(n)
    
class SurveyView(FlaskView):
    def __init__(self):
        super(FlaskView, self).__init__()
        self.question_id_counter = 0   # An impromptu hash
        
    def index(self):
        output = ['<!DOCTYPE html><html><head><title>Active surveys</title></head>']
        output.append('<body><h1>Active Surveys</h1><ul>')
        for survey_id in db:
            output.append('<li><a href="/survey/{0}">{0}</a></lu>'.format(survey_id))
        output.append('</ul></body></html>')
        return '\n'.join(output)
        
    def get(self, survey_id):
        return flask.render_template('submit.html')
            
    @route('<survey_id>/analytics')
    def analytics(self, survey_id):
        survey_id = int(survey_id)
        if survey_id not in db:
            return {}
        else:
            output = copy.deepcopy(db[survey_id])
            for question, response in db[survey_id].items():
                if output[question]['data-type'] in ('bar', 'pie'):
                    output[question]['data'] = collections.Counter(response['data'])
                elif output[question]['data-type'] == 'text':
                    output[question]['data'] = rank_words(' '.join(response['data']), 30)
            json = flask.json.dumps(output)
            return support_jsonp(json)
            
    @route('<survey_id>/report')
    def report(self, survey_id):
        survey_id = int(survey_id)
        responses = db[survey_id] if survey_id in db else {}
        return flask.render_template('report.html', responses=responses)
            
    def post(self, survey_id):
        survey_id = int(survey_id)
        if survey_id not in db:
            db[survey_id] = {}
        attempts = ['text', 'bar', 'pie']
        for value, response in flask.request.form.items():
            if value not in db[survey_id]:
                self._create_new_question(survey_id, value, response, attempts);
                
            db[survey_id][value]['data'].append(response)
            
        flask.flash('Submitted')
        return flask.redirect('survey')
        
    def _create_new_question(self, survey_id, value, response, attempts):
        if len(attempts) == 0:
            attempt = 'bar'
        else:
            attempt = attempts.pop()
            
        db[survey_id][value] = {
            'display': {
                'default': attempt,
                'height': 300,
                'width': 400
            },
            'data': [],
            'data-type': self._determine_data_type(attempt),
            'unique-id': "question-{0}".format(self.question_id_counter),
        }
        self.question_id_counter += 1
        
    def _determine_data_type(self, attempt):
        return attempt
    
if __name__ == '__main__':
    SurveyView.register(app)
    app.run(debug=True)