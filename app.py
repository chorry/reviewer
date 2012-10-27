from __future__ import with_statement
from contextlib import closing
from flask import Flask, request, json, session, g, redirect, url_for, abort,\
    render_template, flash
from werkzeug.wrappers import Request as RequestBase
from werkzeug.contrib.wrappers import JSONRequestMixin

class Request(RequestBase, JSONRequestMixin):
  pass

from Models.database import db_session, init_db
import Models

from flaskext.cache import Cache

from datetime import datetime

from pprint import pprint

import json
import sys

from sqlalchemy import Column, Integer, String

#import models
from Models import *
from vcs.svn import *
from vcs.dummy import *

import ConfigParser

# configuration
config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

SVN_ROOT = config.get('svn','svn_http_root')
#SVN_ROOT = config.get('svn', 'svn_ssh_root')
SVN_USERNAME = config.get('svn', 'login')
SVN_PASSWORD = config.get('svn', 'password')
SVN_HEADER_ENCODING = 'utf-8'
DO_AUTH = True
SAVE_AUTH = False
DEBUG = True
DATABASE_PATH = config.get('database','dbpath')

# init app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('DIFFER_SETTINGS', silent=True)
cache = Cache(app)
#cache config
CACHE_TYPE = 'filesystem'
CACHE_DIR  ='/tmp/'

app.secret_key = 'seeeecret'
#init db

Models.vcsFactory.setVcsParams('svn', password=SVN_PASSWORD).setVcsParams('svn', username=SVN_USERNAME)
@app.before_request
def before_request():
  return

@app.teardown_request
def teardown_request(exception):
  db_session.remove()

@app.template_filter()
def datetimeformat(value, format):
    return datetime.fromtimestamp(value).strftime(format)

#ROUTING
@app.route('/')
@app.route('/dashboard')
def show_activity():
  content = [
      {
      'day': 1343428595.4,
      'action': [{
        'author': {'img': None, 'name': 'Chorry'},
        'time': 1343428595.4,
        'action_text': 'changed 1 file (templates/activity.html)',
        'action_comment': 'new template for activity section'
      }]
    },
      {
      'day': 1343408595.4,
      'action': [{
        'author': {'img': None, 'name': 'Chorry'},
        'time': 1343408595.4,
        'action_text': 'changed 1 file (templates/review.html)',
        'action_comment': 'new template for review section'
      }]
    },
  ]

  return render_template('activity.html', content=content)

@app.route('/source/', defaults={'repoId':'', 'repoUrl':''})
@app.route('/source/<repoId>', defaults={'repoUrl':''})
@app.route('/source/<repoId>//<path:repoUrl>')
@app.route('/source/<repoId>/<path:repoUrl>')
def show_source(repoId, repoUrl):

  #get repo list
  repoModel = RepoModel()
  repoLog = []
  data = { 'repolist' : repoModel.getRepoList(), 'tree' : {} }
  if repoId is not None:
    data['activeRepoId'] = str(repoId)
    try:
      Models.vcsFactory.setVcsParams('svn', repoId=repoId)
      tree = Models.vcsFactory.getVcsModel('svn').getRepositoryTree(repoUrl,'head')
    except Exception, err:
      tree=[]
      print "show_source exception:" + str(err)
      pass

    data['tree'] = tree

    #get short log
    try:
      repoLog = Models.vcsFactory.getVcsModel('svn').getRepositoryLog( repoUrl )
    except Exception, err:
      print "Failed repolog due " + str(err)
      repoLog = [{'error': 'Failed fetching messages due ' + str(err) }]


#  for i in range(len(repoLog)):
#    if 'message' in repoLog[i]:
#      repoLog[i]['message'] = repoLog[i]['message'].decode('cp1251') #TODO: fix broken encoding incoming from server
      #print ("new msg: " + repoLog[i]['message'])
#    else:
#      print "no attr"

  return render_template('source/repoBrowser.html', content=data, repositoryLog = repoLog, repoUrl = repoUrl)

@app.route('/reviews')
def show_review_list():
  rm = ReviewModel()
  reviews = rm.getReviewList()
  orphans = rm.getReviewItemsPendingList()
  revObjects = []
  if reviews is not None:
    for i in reviews:
      revObjects.append(i.getReview())
      pprint (i.getReview())

  data = {'reviews': revObjects, 'orphans': orphans }
  return  render_template('reviews/reviewList.html', content=data)


@app.route('/review/<review_id>')
def show_review(review_id):
    fileList = ReviewModel().getReview(review_id, with_items=True)
    pprint(fileList)
    return render_template(
      'reviews/review.html',
      content=fileList
    )

@app.route('/get/diff/<repoId>/<path:fileName>/<revision1>/<revision2>')
def getFileDiff(repoId, fileName, revision1, revision2):
    Models.vcsFactory.setVcsParams('svn', repoId=repoId)
    diff = Models.vcsFactory.getVcsModel('svn').getFileDiff(fileName, revision1, revision2)
    pprint(diff)
    if 'error' in diff:
      return render_template('differror.html', content=diff)

    return render_template('diffview.html', content=diff)

@app.route('/ajax/addRepo/<repoType>/<path:repoAddr>')
def ajax_addRepository(repoType,repoAddr):
  res = RepoDB.query.filter_by(type=repoType, address=repoAddr).first()
  if res is None:
    r = RepoDB(repoType, repoAddr)
    db_session.add(r)
    db_session.commit()
    response = 'Ok'
  else:
    response = 'Already exists'
  return response

@app.route('/ajax/getRepoList')
def ajax_getRepositoryList():
  return json.dumps( RepoModel().getRepoList() )

@app.route('/ajax/addReviewItem/<vcs_id>//<rev1>/<rev2>', defaults={'author':'', 'filecount': 0 })
@app.route('/ajax/addReviewItem/<vcs_id>/<author>/<rev1>/<rev2>/<filecount>')
def ajax_addReview(vcs_id,author,rev1,rev2, filecount):
  """
  Create orphaned item from commit
  @param vcs_id:
  @param author:
  @param rev1:
  @param rev2:
  @filecount
  @return:
  """
  return json.dumps( ReviewModel().addReviewItem(vcs_id, author, rev1, rev2, filecount) )

@app.route('/ajax/addReviewItems', methods=["POST"])
def ajax_addReviewPOST():
  """
  Create review from orphans
  @return:
  """
  rmodel = ReviewModel()
  reviewId = rmodel.createReview('author','ordinary')
  try:
    for a in request.json:
      pprint(a)
      rmodel.addReviewItemToReview(reviewId, a['itemid'])
    #ReviewModel().addReviewItem(vcs_id, author, rev1, rev2)
    result = { 'success':True, 'message': 'Done'}
  except Exception, err:
    result = {'success':False, 'message':'Error:' + str(err)}

  return json.dumps(result)

@app.route('/ajax/getReviewFiles/<review_id>')
def ajax_getReviewFiles(review_id):
  fileList = ReviewModel.getReviewListItems(review_id)
  return json.dumps(fileList)

@app.route('/ajax/getPathLog/<vcs_id>/<path:path>//<rev1>/<rev2>', defaults={'author': None})
@app.route('/ajax/getPathLog/<vcs_id>/<path:path>/<author>/<rev1>/<rev2>')
def ajax_getPathLog(vcs_id, path, author, rev1, rev2):
  """
  Returns vcs log for path between revision
  @param vcs_id:
  @param path:
  @param rev1:
  @param rev2:
  @return:
  """
  repoModel = RepoModel()
  data = { 'repolist' : repoModel.getRepoList() }
  print path
  Models.vcsFactory.setVcsParams('svn', repoId=vcs_id)

  #get short log
  repoLog = Models.vcsFactory.getVcsModel('svn').getRepositoryLog(
    pathUrl=path,
    type='revision',
    params={
      'rev1':rev1,
      'rev2':rev2,
      'author': author
    }
  )

  return json.dumps(repoLog)

@app.route('/test')
@app.route('/test/')
def test():
  d = { 'r_to'  :'56381',
    'r_from':'56381',
    'path'  : '/labs/branches/Dev_1.0.0.55605/modules/',
    'author' :'nsadovnikova'
  }

  out = ReviewModel().getFilesDiff(rev_from=d['r_from'], rev_to=d['r_to'], author=d['author'], filepath=d['path'])
  return 'hello'

if __name__ == '__main__':
    init_db()
    app.run()