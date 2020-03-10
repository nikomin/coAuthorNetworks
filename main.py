#!/usr/bin/env python3

"""
Analysis of co-authorships between publications taken from a bibtex file.
"""
import bibtexparser
from bibtexparser.customization import splitname
from bibtexparser.latexenc import latex_to_unicode


def genAuthorIDs(authorNames):
    """ Return a unique ID for each name in given list. """
    authorIDs = []
    for authorName in authorNames:
        tmp = splitname( latex_to_unicode(authorName) )
        authorIDs.append( tmp["last"][0]+tmp["first"][0] )
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

def printResults( authorNetwork, authorList ):
    """ Print authorList and -network. """
    print( "======================================================================")
    print( "author, papercount" )
    for authorID in authorList.keys():
        print( "%s,%i" %(authorID, authorList[authorID]["papercount"]) )

    print( "======================================================================")
    print( "source,target,weight" )

    for author in authorNetwork.keys():
        for coAuthor in authorNetwork[author].keys():
            print(author+","+coAuthor+","+str(authorNetwork[author][coAuthor]))
    return



if __name__ == '__main__':
    # read file
    filename = 'phd.bib'
    with open(filename) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file,parser = bibtexparser.bparser.BibTexParser(common_strings=True))

    # parse entries
    authorList = dict() # for number of papers for each author
    authorNetwork = dict() # for number of links between pairs of authors
    ignoredEntriesCount = 0 # entries in bib_database that did not have "author"-field
    for e in bib_database.entries:
        try:
            list_authors=e["author"].split(" and ")
            authorIDs = genAuthorIDs( list_authors )
            for i, author_a_id in enumerate( authorIDs ):
                if not( author_a_id in authorList.keys() ):
                    authorList[ author_a_id ] = {'papercount': 0}
                authorList[ author_a_id ]['papercount'] += 1
                for author_b_id in authorIDs[i+1:]:
                    addCoauthorEdge( authorNetwork, author_a_id, author_b_id)
        except KeyError as e:
            # entries without 'author' are ignored
            ignoredEntriesCount += 1
            pass

    # print results
    print( "# total entries: %i\n# ignored entries: %i"  %( len(bib_database.entries),ignoredEntriesCount ) )
    print( "# authors: %i" %len(authorNetwork.keys()) )
    printResults( authorNetwork, authorList )
