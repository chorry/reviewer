from vcs import VCS
from Parser.Parser import *

__author__ = 'Chorry'

class Dummy(VCS):
    def __init__(self):
        pass

    def setVCSRoot(self, addr):
        self.vcsroot = addr
        return self

    def getVCSRoot(self):
        return self.vcsroot

    def setAuth(self, login, password):
        self.login = login
        self.password = password
        return

    def setEncoding(self, encoding):
        self.encoding = encoding
        return

    def getEncoding(self):
        return self.encoding

    def getRepositoryHead(self):
        super(SVN, self).getRepositoryHead()
        raise NotImplementedError('not implemented yet')

    def getRepositoryStatus(self):
        raise NotImplementedError('not implemented yet')

    def getRepositoryRevisionLog(self, path, revisionFromValue, revisionToValue):
        """
        Returns RevisionLog object for
        """
        revisionFromKind = revisionToKind = 'number'

        if revisionFromValue is None:
            revisionFromKind = 'head'

        if revisionToValue is None:
            revisionToKind = 'unspecified'

        revisionFrom = Revision(revisionFromKind, revisionFromValue)
        revisionTo = Revision(revisionToKind, revisionToValue)

        log = RevisionLog(
            self.client.log(path, revision_start=revisionFrom.getObject(), revision_end=revisionTo.getObject(),
                discover_changed_paths=True))

        return log

    def getRepositoryTree(self, svnUrl, revisionValue, recurse=False):
        #try to convert int to string
        try:
            revisionValue = int(revisionValue)
            revision = Revision("number", revisionValue).getObject()
        except ValueError:
            revision = Revision("head").getObject()

        entries_list =\
        self.client.list(svnUrl,
            revision=revision,
            recurse=recurse)

        tree = []
        for i in range(len(entries_list)):
            tree.append(
                    {
                    'path': entries_list[i][0].repos_path,
                    'revision': entries_list[i][0].created_rev.number,
                    }
            )

        return tree

    def getRepositoryLog(self, path, days=7):
        """
        Returns log entries for last 7 days (default)
        """
        if days is None:
            days = 7
        timeOffset = time.time() - 60 * 60 * 24 * days
        revisionHead = Revision("head")
        revisionDate = Revision("date", timeOffset)

        log = RevisionLog(
            self.client.log(path, revision_start=revisionHead.getObject(), revision_end=revisionDate.getObject(),
                discover_changed_paths=True))
        return log

    def getFileDiff(self, filename, revisionOld, revisionNew):
        myDiff = '--- COMMITTERS	(revision 3901)\n\
+++ COMMITTERS	(revision 4000)\n\
@@ -6,32 +6,37 @@\n\
# Generate code review page of <workspace> vs <workspace>@HEAD, by using\n\
# codediff.py - a standalone diff tool\n\
#\n\
-# Usage: coderev.sh [file|subdir ...]\n\
+# Usage: cd your-workspace; coderev.sh [file|subdir ...]\n\
#\n\
-# $Id: coderev.sh 4 2008-08-19 05:24:24Z mattwyl $\n\
+# $Id: coderev.sh 10 2008-08-23 09:02:26Z mattwyl $\n';

        parser = Parser(myDiff)
        diffEntities = parser.parseDiff()
        #pprint (diffEntities);
        return diffEntities