#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import functools
import copy
import re

import flask
from flask.ext.classy import FlaskView, route
from flask_sockets import Sockets

import analysis


app = flask.Flask(__name__, static_folder='static')
app.secret_key = ',*\xee\xd6tJ1Ja\xc8D\x9d!-\xa2k\xb6K\x9e\xb8\xff\xd7z\xc3'


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
        'should', 'would', 'did', 'does', 'do', 'but', 'yet', 'nor', 'it', 'was', '',
        'its', 'we', 'all', 'in', 'to', 'us', 'so'}
    clean = re.sub('[.,-;:]', ' ', words.lower())
    clean = re.sub('[^a-z0-9 ]', '', clean)
    clean = [a for a in clean.split(' ') if a not in boring] 
    # I can't convert 'clean' to a set, since then it would squash duplicate 
    # occurances of a word.
    return collections.Counter(clean).most_common(n)
    
class SurveyView(FlaskView):
    def __init__(self):
        super(FlaskView, self).__init__()
        
    def index(self):
        return 'TODO: Write up instructions'
        
    def get(self, survey_id):
        return flask.render_template('submit.html')
            
    @route('<survey_id>/analytics')
    def analytics(self, survey_id):
        survey = analysis.Survey(survey_id)
        results = analysis.ResultsView(survey)
        return support_jsonp(flask.json.dumps(results.json()))
            
    @route('<survey_id>/report')
    def report(self, survey_id):
        survey = analysis.Survey(survey_id)
        results = analysis.ResultsView(survey)
        return flask.render_template('report.html', results=results)
    
    
if __name__ == '__main__':
    SurveyView.register(app)
    app.run(debug=True)