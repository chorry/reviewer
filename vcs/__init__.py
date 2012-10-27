from abc import ABCMeta, abstractmethod, abstractproperty

class VCS:
  __metaclass__=ABCMeta

  @abstractmethod
  def getRepositoryStatus(self):
    """
    Returns true if repository is available,
    false otherwise
    """

  @abstractmethod
  def getRepositoryLogByRevision(self, path, revision1, revision2):
    """
    Return list of changed files for specified revision
    """
  @abstractmethod
  def getRepositoryLogByDate(self, path, dateFrom, dateTo):
    """
    Return list of changed files between specified dates
    """

  @abstractmethod
  def getRepositoryHead(self):
    """
    return head revision number
    """
  @abstractmethod
  def getRepositoryTree(self, depth, revisionValue, recurse):
    """
    return tree list of repo
    """

  @abstractmethod
  def getFileDiff(self, filename, revisionOld, revisionNew):
    """
    get diff for provided filename
    """


class VCSClient:
  def __init__(self):
    return

  def setClientType(self, clientType):
    self.client = clientType
    return self

  def getClient(self):
    return self.client

  def getVCSRoot(self):
      return self.VCSRoot

  def setVCSRoot(self, addr):
      self.VCSRoot = addr
      return self

