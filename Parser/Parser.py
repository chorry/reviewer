from pprint import pprint

class Parser(object):
    """
    Parser for diff output
    """

    def __init__(self, data):
        self.data = data
        self.lines = data.splitlines()


    def parseDiff(self):
        # Look for diff headers
        i = 0
        headers = []
        diffs = []
        #text = []
        while i < len(self.lines):
            try:
                diffHeader = self.findDiffHeader(i)
                if diffHeader != False:
                    headers.append(diffHeader)
                    i += 1 #skip already parsed line
                    if len(headers) > 1:
                      diffs.append(
                        DiffCompareEntity(
                          headers[0],
                          self.parseDiffText(headers[0]['line'], headers[1]['line'])
                        )
                      )
                      headers.pop(0)
                else:
                    #text.append( self.parseDiffLine(self.lines[i]) )
                    # diffs[-1].addLine = self.parseDiffLine
                    #    pass
                    pass
            except Exception as e:
                #TODO: find out what to do with this exception
                print "#" + str(i) + " has error for line " + str(i) + ": " + e.message
                print "line content: " + self.lines[i]
                pass
            i += 1

        if len(headers) > 0:
            diffs.append(
                DiffCompareEntity(headers[0], self.parseDiffText(headers[0]['line'], None))
            )

        return diffs

    def findDiffHeader(self, lineNum):
        """
        returns parsed header and it's line number
        """
        if lineNum + 1 < len(self.lines) and\
           (
               (
                   self.lines[lineNum].startswith('--- ') and
                   self.lines[lineNum + 1].startswith('+++ ')
                   )
               or
               (
                   self.lines[lineNum].startswith('*** ') and
                   self.lines[lineNum + 1].startswith('--- ') and not
                   self.lines[lineNum].endswith(" ****")
                   )
               ):
            try:
                data = {'old': {}, 'new': {}}
                data['old']['file'], data['old']['rev'] = self.parseDiffStringHeader(
                    self.lines[lineNum][4:]) #we dont need no '+++ '
                data['new']['file'], data['new']['rev'] = self.parseDiffStringHeader(
                    self.lines[lineNum + 1][4:]) # and '--- ' too
                data['line'] = lineNum
                return data
            except ValueError as VE:
                raise Exception('Fail:' + VE.message)
        return False

    def parseDiffStringHeader(self, string):
        """
        Finds filename in diff header string (i.e '--- configs/config.php	(revision 54597)')
        """
        if "\t" in string:
            # If there is a tab, split by it
            fname, r = string.split("\t")
            tmp, r = r[:-1].split(" ")
            return [fname, r]

        # If there are spaces only
        if "  " in string:
            return string.split(r"  +", string, 1)
        return

    def parseDiffText(self, lineFrom, lineTo):

        if lineTo is not None:
          drange =  self.lines[lineFrom + 2:lineTo]
        else:
          drange = self.lines[lineFrom + 2:]

        text = []
        i = 0
        while i < len(drange):
          text.append(self.parseDiffLine(drange[i]))
          i += 1
        return text

    def parseDiffLine(self, line):
      """
      Parse diff line to find its type
      """
      if line[0] == '-':
        type = 'del'
      elif line[0] == '+':
        type = 'add'
      else:
        type = 'none'

      return {'type': type, 'line': line}


class DiffCompareEntity:
    def __init__(self, header, text):
        self.header = header
        self.text = text
        return

    def addLine(self, line):
        self.text.append(line)

    def getHeader(self):
        return self.header

    def getDiff(self):
        return self.text
