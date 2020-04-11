#!/usr/bin/env python3
"""
Analysis of co-authorships between publications taken from a bibtex file.
"""
import bibtexparser
from bibtexparser.customization import splitname
from bibtexparser.latexenc import latex_to_unicode

from sys import argv
from os import path

extensionDefault_authorlist = ".authorlist.csv"
extensionDefault_authorNetwork = ".authorNetwork.csv"
extensionDefault_paperlist = ".paperlist.csv"
extensionDefault_paperNetwork = ".paperNetwork.csv"
extensionDefault_report = ".report.md"
extensionDefault_histogram = ".histogram.png"

def readBibtexfile(filename):
    """Return a bib_database from File"""
    with open(filename) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file,parser = bibtexparser.bparser.BibTexParser(common_strings=True))
    return bib_database


def genAuthorIDs(authorNames):
    """ Return a unique ID for each name in given list. """
    authorIDs = []
    for authorName in authorNames:
        tmp = splitname( latex_to_unicode(authorName) )
        tmpFirstname = ''
        try:
            tmpFirstname = tmp["first"][0]
        except IndexError:
            # leave empty, if no first name is give. it ncould still work
            pass
        authorIDs.append( tmp["last"][0]+tmpFirstname )
    return authorIDs

def addCoauthorEdge( authorNetwork, author_a_id, author_b_id):
    """ Adds an edge between author_a and author_b to the authorNetwork."""
    if author_a_id != author_b_id:
        if not( author_a_id in authorNetwork.keys() ):
            authorNetwork[author_a_id] = dict()
        if not( author_b_id in authorNetwork[author_a_id] ):
            authorNetwork[author_a_id][author_b_id] = 0
        if not( author_b_id in authorNetwork.keys() ):
            authorNetwork[author_b_id] = dict()
        if not( author_a_id in authorNetwork[author_b_id] ):
            authorNetwork[author_b_id][author_a_id] = 0
        authorNetwork[author_a_id][author_b_id] += 1
        authorNetwork[author_b_id][author_a_id] += 1
    return

def addCoPaperEdge( paperNetwork, paper_i, paper_j ):
    """ Adds an edge between to papers that share an author. """
    if not( paper_i in paperNetwork.keys() ):
        paperNetwork[paper_i] = dict()
    if not( paper_j in paperNetwork[paper_i] ):
        paperNetwork[paper_i][paper_j] = 0
    if not( paper_j in paperNetwork.keys() ):
        paperNetwork[paper_j] = dict()
    if not( paper_i in paperNetwork[paper_j] ):
        paperNetwork[paper_j][paper_i] = 0
    paperNetwork[paper_i][paper_j] += 1
    paperNetwork[paper_j][paper_i] += 1
    return

def extractNetworks( bib_database ):
    """Parses all bibtex-entries and analyses links between authors
    and papers. Returns networks and lists."""
    # parse entries
    authorList = dict() # for number of papers for each author
    authorNetwork = dict() # for number of links between pairs of authors
    paperList = dict()
    paperNetwork = dict()

    ignoredEntriesCount = 0 # entries in bib_database that did not have "author"-field
    for e in bib_database.entries:
        # find authors and counts of papers and of co-authorships
        try:
            authorIDs = genAuthorIDs( e["author"].split(" and ") )
            paperList[e['ID']] = { 'authorIDs' : authorIDs, 'year' : e['year'] }
            for i, author_a_id in enumerate( authorIDs ):
                if not( author_a_id in authorList.keys() ):
                    authorList[ author_a_id ] = {'papercount': 0}
                authorList[ author_a_id ]['papercount'] += 1
                for author_b_id in authorIDs[i+1:]:
                    addCoauthorEdge( authorNetwork, author_a_id, author_b_id )
        except KeyError as e:
            # entries without 'author' are ignored
            ignoredEntriesCount += 1
            pass

    # pairs of papers
    for i, paper_i in enumerate( list(paperList.keys()) ):
        for paper_j in list(paperList.keys())[i+1:]:
            for author_i in paperList[paper_i]["authorIDs"]:
                try:
                    tmp = paperList[paper_j]["authorIDs"].index( author_i )
                    # entry found, we have one connection
                    addCoPaperEdge( paperNetwork, paper_i, paper_j )
                except ValueError:
                    # papers don't share author
                    pass

    return authorNetwork, authorList,  paperNetwork, paperList, ignoredEntriesCount


def writePapers( filenameBase, paperList, paperNetwork ):
    """ Write csv of paperList and -network to files.
            paperList: paperID,authorcount,year
            paperNetwork: source,target,weight,relativeWeight"""

    outfilename = filenameBase + extensionDefault_paperlist
    print( "saving paperlist to %s" %outfilename)
    f = open( outfilename, "w")
    f.write( "paper,authorcount,year\n" )
    for paperID in paperList.keys():
        f.write( "%s,%i,%s\n" %(paperID, len(paperList[paperID]['authorIDs']), paperList[paperID]['year'] ) )
    f.close()

    outfilename = filenameBase + extensionDefault_paperNetwork
    print( "saving papernetwork to %s" %outfilename)
    f = open( outfilename, "w")
    f.write( "source,target,weight,relativeWeight\n" )
    for paper in paperNetwork.keys():
        for coPaper in paperNetwork[paper].keys():
            absoluteWeight = paperNetwork[paper][coPaper]
            relativeWeight = absoluteWeight/len(paperList[paper]['authorIDs'])
            f.write(paper+","+coPaper+","+str(absoluteWeight)+","+str(relativeWeight)+'\n')
    f.close()
    
    return

def writeAuthors( filenameBase, authorList, authorNetwork ):
    """ Write csv of paperList and -network to files.
            authorList: author,papercount
            authorNetwork: source,target,weight"""

    outfilename = filenameBase + extensionDefault_authorlist
    print( "saving authorlist to %s" %outfilename)
    f = open( outfilename, "w")
    f.write( "author,papercount\n" )
    for authorID in authorList.keys():
        f.write( "%s,%i\n" %(authorID, authorList[authorID]["papercount"]) )
    f.close()

    outfilename = filenameBase + extensionDefault_authorNetwork
    print( "saving authornetwork to %s" %outfilename)
    f = open( outfilename, "w")
    f.write( "source,target,weight\n" )
    for author in authorNetwork.keys():
        for coAuthor in authorNetwork[author].keys():
            f.write(author+","+coAuthor+","+str(authorNetwork[author][coAuthor])+'\n')
    f.close()

    
    return


import networkx as nx
def makePaperGraph( paperList, paperNetwork ):
    """Returns graph linking papers when they share authors."""
    G = nx.Graph()
    for paper in paperList.keys():
        G.add_node(paper)
    for paper in paperNetwork.keys():
        for copaper in paperNetwork[paper]:
            edge = (paper,copaper)
            G.add_edge(*edge)
    return G


import matplotlib.pyplot as plt
import numpy as np
def drawHistogram( filenamebase, paperList, largestComp ):
    """Writes histogram of papers to png-file."""
    years=[]
    for paper in paperList.keys():
        try:
            years.append(int(paperList[paper]['year']))
        except ValueError as e:
            print(e)
    years.sort()
    num_bins = np.linspace(years[0],years[-1],years[-1]-years[0]) # one bin per year
    n,bins,patches = plt.hist(years, num_bins,alpha=0.5)

    yearsMaxCluster = []
    for paper in largestComp:
        try:
            yearsMaxCluster.append(int(paperList[paper]['year']))
        except ValueError as e:
            print(e)
    yearsMaxCluster.sort()
    n,bins,patches = plt.hist(yearsMaxCluster, num_bins,alpha=0.5)
    plt.savefig(filenamebase+extensionDefault_histogram)
    return

def writeGraphReport( filenameBase, G ):
    """Extract network characteristics and return a report."""
    cc = list(nx.connected_components(G))
    ccSizes = []
    largestComp = cc[0]
    largestCompSize = len(largestComp)
    for i in cc:
        ccSizes.append(len(i))
        if len(i)>largestCompSize: #found a component bigger than the previously biggest
            largestComp = i
            largestCompSize = len(largestComp)
    ccSizes.sort()

    drawHistogram( filenameBase, paperList, largestComp )
    print( "Saving report to %s" %(filenameBase + extensionDefault_report) )
    f = open( filenameBase + extensionDefault_report, "w" )
    f.write( "# Report for %s\n" %filenameBase )
    f.write( "\nYour database was read and has the following general characteristics:\n\n" )
    f.write( "* total publications: %i\n* ignored entries: %i\n"  %( len(bib_database.entries),
                                                            ignoredEntriesCount ) )
    f.write( "* number of authors: %i\n" %len(authorNetwork.keys()) )
    f.write( """\n## Network analysis

The paper network is built by connecting papers that share
authors. If *paper A* shares an author with *paper B* and
*paper B* shares an author with *paper C*, then *A*,*B* and *C* are
in a connected component. **These components might show
communities of researchers.**\n\n""")
    f.write( "* The largest connected component has %i papers, all these papers are connected via people authoring more than one paper.\n" %largestCompSize )
    f.write( "\t* One element of that component is:\n\n`%s`\n\n" %list(largestComp)[0])
    f.write( "* %i papers of your research don't share authors with any other paper.\n" %ccSizes.count(1))
    f.write( "\n![Publications per year (total and of largest component)](%s)\n" %(filenameBase+extensionDefault_histogram) )
    f.close()


    return


if __name__ == '__main__':
    if len(argv) < 2:
        print("Analyse co-authorships in bibtex-files.\n")
        print("Usage:\n\t%s BIBTEXFILENAME" %argv[0])
    else:
        # read file
        filename = argv[1]
        try:
            bib_database = readBibtexfile( filename )
            authorNetwork, authorList,  paperNetwork, paperList, ignoredEntriesCount = extractNetworks( bib_database )

            filenameBase = path.split(filename)[1]
            
            # write results to files
            writePapers( filenameBase, paperList, paperNetwork )
            writeAuthors( filenameBase, authorList, authorNetwork )

            G = makePaperGraph( paperList, paperNetwork )

            # write report
            writeGraphReport( filenameBase, G )


    
            print( "All done." )

        except FileNotFoundError:
            print("File `%s` not found. Aborting." %filename)
