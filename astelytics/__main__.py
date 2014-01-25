#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import functools
import copy

import flask
from flask.ext.classy import FlaskView, route
from flask_sockets import Sockets


app = flask.Flask(__name__, static_folder='static')
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
    
class SurveyView(FlaskView):
    def __init__(self):
        super(FlaskView, self).__init__()
        self.question_id_counter = 0
        
    def index(self):
        output = ['<!DOCTYPE html><html><head><title>Active surveys</title></head>']
        output.append('<body><h1>Active Surveys</h1><ul>')
        for survey_id in db:
            output.append('<li><a href="/survey/{0}">{0}</a></lu>'.format(survey_id))
        output.append('</ul></body></html>')
        return '\n'.join(output)
        
    def get(self, survey_id):
        survey_id = int(survey_id)
        if survey_id not in db:
            return 'Error -- Not found.'
        else:
            output = output = ['<!DOCTYPE html><html><head>']
            output.append('<title>Survey {0}</title></head>'.format(survey_id))
            output.append('<body><h1>Survey {0}</h1><ul>'.format(survey_id))
            for question, answer in db[survey_id].items():
                output.append('<li>{0}: {1}</li>'.format(question, answer))
            output.append('</ul></body></html>')
            return '\n'.join(output)
            
    @route('<survey_id>/analytics')
    def analytics(self, survey_id):
        survey_id = int(survey_id)
        if survey_id not in db:
            return {}
        else:
            output = copy.deepcopy(db[survey_id])
            for question, response in db[survey_id].items():
                output[question]['data'] = collections.Counter(response['data'])
            json = flask.json.dumps(output)
            return support_jsonp(json)
            
    @route('<survey_id>/report')
    def report(self, survey_id):
        survey_id = int(survey_id)
        return flask.render_template('report.html', responses=db[survey_id])
            
    def post(self, survey_id):
        survey_id = int(survey_id)
        if survey_id not in db:
            db[survey_id] = {}
        attempts = ['bar', 'pie']
        for value, response in flask.request.form.items():
            if value not in db[survey_id]:
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
                    'unique-id': "question-{0}".format(self.question_id_counter),
                }
                self.question_id_counter += 1
                
            db[survey_id][value]['data'].append(response)
        return 'Done, {0}'.format(survey_id)
    
if __name__ == '__main__':
    SurveyView.register(app)
    app.run(debug=True)