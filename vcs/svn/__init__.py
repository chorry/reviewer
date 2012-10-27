import os.path
from os.path import isdir, isfile, dirname, islink, realpath
from datetime import datetime
import time
import pysvn
from vcs import VCS
from abc import ABCMeta, abstractmethod, abstractproperty
from pprint import pprint
from Parser.Parser import *

class Revision:

    KINDS = {
        "unspecified":      pysvn.opt_revision_kind.unspecified,
        "number":           pysvn.opt_revision_kind.number,
        "date":             pysvn.opt_revision_kind.date,
        "committed":        pysvn.opt_revision_kind.committed,
        "previous":         pysvn.opt_revision_kind.previous,
        "working":          pysvn.opt_revision_kind.working,
        "head":             pysvn.opt_revision_kind.head,
        "base":             pysvn.opt_revision_kind.base
    }

    def __init__(self, kind, value=None):
        self.kind = unicode(kind).lower()
        self.value = value
        self.is_revision_object = True

        if self.value is None and self.kind in ("number", "date"):
            self.kind = "head"

        self.__revision_kind = self.KINDS[self.kind]
        self.__revision = None

        try:
            if value is not None:
                self.__revision = pysvn.Revision(self.__revision_kind, value)
            else:
                self.__revision = pysvn.Revision(self.__revision_kind)
        except Exception, e:
          pprint (e)

    def __unicode__(self):
        if self.value:
            return unicode(self.value)
        else:
            return self.kind

    def short(self):
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()

    def getObject(self):
        return self.__revision

class RevisionLog:
  def __init__(self, pysvnLogObject):
    self.collection = []
    if pysvnLogObject is not None:
      for i in range( len(pysvnLogObject) ):
        paths = []
        for a in range ( len(pysvnLogObject[i]['changed_paths']) ):
          paths.append(
            { 'path':pysvnLogObject[i]['changed_paths'] [a]['path'],
              'action' : pysvnLogObject[i]['changed_paths'] [a]['action']
            }
          )

        self.collection.append( { 'revision': pysvnLogObject[i].revision.number,
                               'author'  : pysvnLogObject[i]["author"],
                               'changed_paths' : sorted(paths),
                               'date'    : pysvnLogObject[i]["date"],
                               'message' : pysvnLogObject[i]["message"] } )

      self._max = len(pysvnLogObject) - 1
    else:
      self._max = 0
      self._current = 0

  def __iter__(self):
    return self

  def valid(self):
    if self._current < self._max:
      return True
    return False

  def rewind(self):
    self._current = 0
    return

  def next(self):
    if self._current > self._max:
      raise StopIteration
    else:
      self._current += 1
      return self._current - 1

  def current(self):
    return self.collection[self._current]

  def setLog(self, array):

    if not isinstance(array, basestring):
      self.max = len(array)
      self.collection = array
      return self
    else:
      return Exception('Not an array')

  def getLog(self):
    return self.collection

class RepositoryTree:
  def __init__(self, collection, vcsRoot):
    self.collection = []
    self.vcsRoot = vcsRoot
    self.setTree(collection)

  def getTree(self):
    return self.collection

  def setTree(self, collection):
    for i in range( len(collection)):
      #if self.vcsRoot is not None:
        #collection[i][0].repos_path = collection[i][0].repos_path.replace(self.vcsRoot,"_")
      self.collection.append(
        {
        'path': collection[i][0].repos_path[1:],
        'revision' : collection[i][0].created_rev.number,
        }
      )
    return self

class SVN(VCS):
    """
    SVN Wrapper class
    """

    def __init__(self):
        self.client = pysvn.Client()
        self.interface = "pysvn"
        self.client.callback_get_login = self.svn_get_login

    def setVCSRoot(self, addr):
      self.vcsroot = addr
      return self

    def getVCSRoot(self):
      return self.vcsroot


    def setAuth(self,login, password):
      self.login = login
      self.password = password
      return self

    def setEncoding(self, encoding):
      self.encoding = encoding
      return

    def getEncoding(self):
      return self.encoding

    def svn_get_login( self, realm, username, may_save ):
      return True, self.login, self.password, False

    def getRepositoryHead(self):
      super(SVN, self).getRepositoryHead()
      raise NotImplementedError('not implemented yet')

    def getRepositoryStatus(self):
      raise NotImplementedError('not implemented yet')

    def getRepositoryTree(self, svnUrl, revisionValue, recurse=False):
      print "getting tree for " + svnUrl
      #try to convert int to string
      try:
        revisionValue = int(revisionValue)
        revision = Revision ("number", revisionValue).getObject()
      except ValueError:
        revision = Revision ("head").getObject()

      tree = RepositoryTree(
        self.client.list( svnUrl,
          revision=revision,
          recurse=recurse ),
        self.getVCSRoot()
      )

      return tree

    def getRepositoryLogByRevision(self, path, revisionFromValue, revisionToValue, author, limit=0):
      """
      Returns RevisionLog object between revisions
      revisionFromValue default: head
      revisionToValue   default: unspecified
      @return RevisionLog/False
      """
      revisionFromKind = revisionToKind = 'number'

      if revisionFromValue is None:
        revisionFromKind = 'head'

      if revisionToValue is None:
        revisionToKind = 'unspecified'

      revisionFrom = Revision(revisionFromKind, revisionFromValue)
      revisionTo   = Revision(revisionToKind, revisionToValue)

      log = RevisionLog ( self.client.log(path, revision_start=revisionFrom.getObject(), revision_end=revisionTo.getObject(), discover_changed_paths=True, limit=limit) )
      filteredLog = ''

      if author is not None:
        for i in log.getLog():
          if i['author'] == author:
            if not filteredLog:
              filteredLog = []
            filteredLog.append(i)
        if not filteredLog:
          return False

        log = RevisionLog(None).setLog(filteredLog)

      return log

    def getRepositoryLogByDate(self, path, dateFrom = None, dateTo = None, limit=0):
      """
      Returns RevisionLog object between dates
      path      string
      dateFrom  unixtime  (default: now)
      dateTo    unixtime  (default: 3 days before dateFrom)
      """
      if dateFrom is None:
        revisionHead = Revision ( "head" )
        dateFrom = time.time()
      else:
        revisionHead = Revision ( "date", dateFrom)

      if dateTo is None:
        dateTo = 60*60*24*3

      timeOffset = dateFrom - dateTo
      revisionDate = Revision ( "date", timeOffset )

      log = RevisionLog ( self.client.log(path, revision_start=revisionHead.getObject(), revision_end=revisionDate.getObject(), discover_changed_paths=True, limit=limit) )
      return log

    def getFileDiff(self, filename, revisionOld, revisionNew):
      """
      @revisionOld: string
      @revisionNew: string
      """
      revisionNew = Revision ("number", revisionNew).getObject()
      revisionOld = Revision ("number", revisionOld).getObject()
      tmpPath = "."
      recurseFlag = False

      myDiff =\
      self.client.diff(
        tmpPath,
        filename,
        revision1=revisionOld,
        url_or_path2=filename,
        revision2=revisionNew,
        recurse=recurseFlag,
        ignore_ancestry=False,
        diff_deleted=True,
        ignore_content_type=False,
        #header_encoding=self.getEncoding(),
      )

      parser = Parser(myDiff)
      diffEntities = parser.parseDiff()

      return diffEntities
