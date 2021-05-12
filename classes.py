class Bibliography:
    filenamebase = None
    authorList = dict() # for number of papers for each author
    authorNetwork = dict() # for number of links between pairs of authors
    paperList = dict()
    paperNetwork = dict()
    ignoredEntriesCount = 0 # entries in bib_database that did not have "author"-field
    totalEntriesCount = 0
    graphOfPapers = None


class Report:
    bibfilename = None
    totalPubs = None
    ignoredPubs = None
    nrAuthors = None
    maxCC = None
    maxCCsize = None
    maxCCsizePerTotal = None
    maxCCelement = None
    secondCCsize = None
    secondCCsizePerTotal = None
    numberUnconnectedPapers = None
    unconnectedPapersPerTotal = None
    histogramOutfilename = None

    
    raw = """# Report for {bibfilename}
Your database was read and has the following general characteristics:

* total publications: {totalPubs}
* ignored entries: {ignoredPubs}
* number of authors: {nrAuthors}

## Network analysis

The paper network is built by connecting papers that share
authors. If *paper A* shares an author with *paper B* and
*paper B* shares an author with *paper C*, then *A*,*B* and *C* are
in a connected component. **These components might show
communities of researchers.**

* The largest connected component has {maxCCsize} ({maxCCsizePerTotal:.0%}) papers:

    {maxCC}

* the second largest group contains {secondCCsize} ({secondCCsizePerTotal:.0%}) papers.
* {numberUnconnectedPapers} papers ({unconnectedPapersPerTotal:.0%}) of your research don't share authors with any other paper.

![Publications per year (total and of largest component)]({histogramOutfilename})"""

    def text(self):
        return self.raw.format(bibfilename = self.bibfilename,
                               totalPubs = self.totalPubs,
                               ignoredPubs = self.ignoredPubs,
                               nrAuthors = self.nrAuthors,
                               maxCCsize = self.maxCCsize,
                               maxCCsizePerTotal = self.maxCCsizePerTotal,
                               maxCCelement = self.maxCCelement,
                               maxCC = self.maxCC,
                               secondCCsize = self.secondCCsize,
                               secondCCsizePerTotal = self.secondCCsizePerTotal,
                               numberUnconnectedPapers = self.numberUnconnectedPapers,
                               unconnectedPapersPerTotal = self.unconnectedPapersPerTotal,
                               histogramOutfilename = self.histogramOutfilename)
