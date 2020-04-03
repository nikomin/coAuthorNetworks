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
    
            # write report
            print( "Saving report to %s" %(filenameBase + extensionDefault_report) )
            f = open( filenameBase + extensionDefault_report, "w" )
            f.write( "# Report for %s\n" %filenameBase )
            f.write( "* total entries: %i\n* ignored entries: %i\n"  %( len(bib_database.entries),
                                                                    ignoredEntriesCount ) )
            f.write( "* number of authors: %i\n" %len(authorNetwork.keys()) )
            f.close()


            print( "Done." )

        except FileNotFoundError:
            print("File `%s` not found. Aborting." %filename)
