from sqlalchemy import Column, Integer, String, ForeignKey
from Models.database import *
from flask import session
from vcs.svn import *
from sqlalchemy.ext.declarative import declarative_base
#Base = declarative_base()
from pprint import pprint
import ConfigParser

# configuration
config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

class Collection:
  def __init__(self, items=None):
    self.low = 0
    self.high = 0
    self.counter = 0
    self.items = []
    if items is not None:
      self.addItem(items)
    return

  def next(self):
    if self.isIterable():
      self.counter += 1
      print self.counter
      return self.items[ (self.counter - 1) ]
    return False

  def prev(self):
    if self.counter > 2:
      self.counter -= 1
      return self.items[self.counter]
    return

  def resetCounter(self):
    self.counter = 0
    return self

  def isIterable(self):
    if self.counter < self.high:
      return True
    return False

  def addItem(self, items):
#    if not isinstance(items, basestring):
#      if len(items) > 0:
#        self.high += len(items)
#        self.low += 1
#    else:
    self.high += 1
    self.low += 1

    self.items.append(items)
    return self

  def getItems(self):
    return self.items

  def getCurrent(self):
    return self.items[self.counter]

  def getCount(self):
    return self.high

class EntityReview:

  def __init__(self):
    self.properties = {}
    self.items = []
    return

  def setReviewParams(self, params):
    pprint (params)
    for atr_name in ['id', 'author', 'fileCount', 'state', 'type']:
      if atr_name in params:
        self[atr_name] = params[atr_name]
    return self

  def __setitem__(self, key, value):
    self.properties[key] = value

  def __getitem__(self, item):
    return self.properties[item]

  def addItem(self, item):
    self.items.append(item);
    return

  def getParam(self, paramName):
    return self[paramName]

  def getReview(self):
    return {
      'properties': self.properties,
      'items':  self.items }
  
class vcsFactory:
  def __init__(self):
    self._instances = {}
    self._params = {'svn': {}, 'git': {}, 'hg': {} }
    return
  
  def getVcsModel(self, type):
    if type == 'svn':
      if self._instances['svn'] is None:
        self._instances['svn'] = self.getVcsModelSvn('svn')
      return self._instances['svn']
    elif type == 'hg':
      if self._instances['hg'] is None:
        self._instances['hg'] = self.getVcsModelSvn()
      return self._instances['hg']
    elif type == 'git':
      if self._instances['git'] is None:
        self._instances['git'] = self.getVcsModelSvn()
      return self._instances['git']
    else:
      return Exception('Unsupported VCS type')

  def setVcsParams(self, type, repoId=None, username=None, password=None):
    if repoId is not None:
      self._params[type]['vcsRoot'] = RepoModel().getRepoRootById(repoId)
    if username is not None:
      self._params[type]['username'] = username
    if password is not None:
      self._params[type]['password'] = password
    return self

  def getVcsModel(self, type):
    return vcsModel(
      SVN().
      setVCSRoot( self._params[type]['vcsRoot'] ).
      setAuth( self._params[type]['username'], self._params[type]['password'] )
    )

  def getVcsModelHg(self):
    return

vcsFactory = vcsFactory()

class vcsModel:
  """
  Basic vcs model for all repositories
  """
  def __init__(self, vcsClient):
    self.client = vcsClient
    return

  def getTest(self):
    return 'Test'

  def getCache(self):
    return self.cache

  def getFileDiff(self, fileName, revision1, revision2):
    try:
      svnUrl = self.client.getVCSRoot() + fileName
      print "Looking for " +revision1 + ":" + revision2 + " at " + svnUrl
      diffEntities = self.client.getFileDiff(svnUrl, revision1, revision2)
      result = []
      for i in range(len(diffEntities)):
        result.append({
          'head': diffEntities[i].getHeader(),
          'diff_text': diffEntities[i].getDiff(),
          })

    except Exception as e:
      result = {'error': e.message}
      pass

    return result

  def getRepositoryTree(self, repoUrl, revision):
    print 'where is cache?'
    vcsUrl = self.client.getVCSRoot() + repoUrl
    return self.client.getRepositoryTree(vcsUrl, revision).getTree()

  def getRepositoryLog(self, pathUrl=None, type=None, params=None):
    """
    type = date/revision (date by default)
    params = dateFrom,dateTo/rev1,rev2
    """
    if pathUrl is None:
      raise  Exception("project url is not set!")

    vcsUrl = self.client.getVCSRoot() + pathUrl

    if type is None or type == 'date':
      dateFrom = dateTo = None
      if isinstance(params, list) and 'dateFrom' in params:
        dateFrom = params['dateFrom']
      if isinstance(params, list) and 'dateTo' in params:
        dateTo = params['dateTo']
      result = self.getRepositoryLogByDate(path=vcsUrl, dateFrom=dateFrom, dateTo=dateTo)
    else:
      result = self.getRepositoryLogByRevisions(vcsUrl, revFrom=params['rev1'], revTo=params['rev2'], filterAuthor=params['author'])

    return result

  def getRepositoryLogByDate(self, path, dateFrom, dateTo):
    print "NO CACHE!"
    return self.client.getRepositoryLogByDate(path, dateFrom, dateTo).getLog()

  def getRepositoryLogByRevisions(self, path, revFrom, revTo, limit=0, filterAuthor=None):
    """
    @param path
    @param revFrom
    @param revTo
    @param limit
    @param filterAuthor
    @return vcs.svn.RevisionLog
    """
    #TODO: add filtering
    log = self.client.getRepositoryLogByRevision(path, revFrom, revTo, limit=limit, author=filterAuthor)
    if log:
      return log.getLog()
    return False

class RepoModel():
  def __init__(self):
    return

  def getRepoList(self):
    try:
      r = RepoDB.query.all()
      if r is not None:
        text = []
        for i in range(len(r)):
          text.append(r[i].getRepo())
      else:
        raise Exception("cant get repo list from db")
    except Exception, err:
      text = { 'exception' : str(err) }

    return text

  def getRepoTypeById(self, repoId):
    return str(RepoDB.query.filter(RepoDB.id == repoId).first().type)

  def getRepoRootById(self, repoId):
    return str(RepoDB.query.filter(RepoDB.id == repoId).first().address)

class ReviewModel():
  def __init__(self):
    return

  def addReviewItem(self, vcs_id, author, rev1, rev2, filecount):
    """
    Adds orphaned item for later review creation
    """
    result = ReviewItemsDB.query.filter_by(vcs_id=vcs_id, r_from=rev1, r_to=rev2, author=author).first()
    if result is None:
      try:
        res = ReviewItemsDB(review_id='', vcs_id=vcs_id, type='ordinary', r_from=rev1, r_to=rev2, author=author, file_count=filecount)
        db_session.add(res)
        db_session.commit()
        out = True
      except Exception, err:
        out =  Exception(err)
    else: #already exists
      out = False
    return out

  def addReviewItemToReview(self, review_id, review_item_id):
    """
    @return bool
    """
    reviewItem = ReviewItemsDB.query.filter_by(id=review_item_id, review_id='').first()
    if reviewItem is not None:
      pprint (reviewItem)
      #TODO add @memoize to review call
      review = ReviewDB.query.filter_by(id=review_id).first()
      if review is not None:
        reviewItem.review_id = review.id
        if review.file_count is None:
          review.file_count = 0
        review.file_count += reviewItem.file_count
        db_session.add(review)
        db_session.add(reviewItem)
        db_session.commit()
        return True
    return False

  def deleteReviewItemFromReview(self, review_id, review_item_id):
    return

  def getReview(self, review_id, with_items=False):
    """
    Returns existent review
    """
    review = ReviewDB.query.filter_by(id=review_id).first()

    if review is not None:
      review = EntityReview().setReviewParams(review.getItem())
      if with_items:
        list = ReviewItemsDB.query.filter_by(review_id=review_id).all()
        for i in list:
          vcsFactory.setVcsParams(
            type   = RepoModel().getRepoTypeById(i.getItem()['vcs_id']),
            repoId = i.getItem()['vcs_id']
          )

          vModel = vcsFactory.getVcsModel(type=RepoModel().getRepoTypeById(i.getItem()['vcs_id']) )

          result = vModel.getRepositoryLogByRevisions(
            path=RepoModel().getRepoRootById(i.getItem()['vcs_id']),
            revFrom=i.getItem()['r_from'],
            revTo=i.getItem()['r_from'],
            filterAuthor=i.getItem()['author']
          )
          #pprint (result)
          review.addItem(result)
    return review.getReview()


  def getReviewItemsPendingList(self):
    """
    return list of orphaned items
    """
    q = ReviewItemsDB.query.filter_by(review_id='').all()
    result = []
    for i in range(len(q)):
      try:
        #count files for each (if cache is working, this should not give much problems for now)
        vcsLog = \
        vcsModel(
            SVN().
            setVCSRoot( RepoModel().getRepoRootById(q[i].getItem()['vcs_id']) ).
            setAuth( config.get('svn','login'), config.get('svn','password') )
          ).getRepositoryLogByRevisions(
            RepoModel().getRepoRootById( q[i].getItem()['vcs_id'] ),
            q[i].getItem()['r_from'],
            q[i].getItem()['r_to']
          )
        a = q[i].getItem()

        a.update( {'count':len(vcsLog[0]['changed_paths']), 'files': vcsLog[0]['changed_paths']} )
        result.append ( a )
      except Exception, e:
        print "Oops, an error:" + str(e)
    return result

  def getReviewList(self, page = None):
    """
    return list of reviews
    """
    try:
      q = ReviewDB.query.all()
      reviewList = []
      for i in q:
        pprint (i.getItem())
        a = EntityReview().setReviewParams( i.getItem() )
        reviewList.append( a  )
    except Exception, e:
      return e
    return reviewList


  def createReview(self, author, type = None):
    """
    Creates an empty review
    """
    if type is None:
      type = ''
    res = ReviewDB(reviewer='', author=author, type=type, items='')
    db_session.add(res)
    db_session.commit()
    return (res.id)

  def getFilesDiff(self, rev_from, rev_to, filepath, author=None):
    """
    return diffs of files in provided filepath in bulk
    """
    vcsRoot = RepoModel().getRepoRootById(2)
    vModel =  vcsModel(
      SVN().
      setVCSRoot( vcsRoot ).
      setAuth( config.get('svn','login'), config.get('svn','password') )
    )

    repLog = vModel.getRepositoryLogByRevisions(vcsRoot + filepath, rev_from, rev_to).pop(0)
    diffs=[]
    for i in range(len(repLog['changed_paths'])):
      if repLog['changed_paths'][i]['action'] == 'M':
        #pprint (repLog['changed_paths'][i])
        if (rev_from == rev_to):
          #okay, get prev revision
          print "Looking for: " + vcsRoot + repLog['changed_paths'][i]['path']
          itemLog = vModel.getRepositoryLogByRevisions(vcsRoot + repLog['changed_paths'][i]['path'], revFrom=rev_from, revTo=0, limit=2)
          pprint (itemLog)
        #diffs.append ( vModel.getFileDiff(  repLog['changed_paths'][i]['path'], rev_from, rev_to) )

    #pprint (diffs)
    return diffs
