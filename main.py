#!/usr/bin/env python3
"""
Analysis of co-authorships between publications taken from a bibtex file.
"""
import bibtexparser
from bibtexparser.customization import splitname
from bibtexparser.latexenc import latex_to_unicode
from sys import argv

extensionDefault_authorlist = ".authorlist.csv"
extensionDefault_authorNetwork = ".authorNetwork.csv"



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

def printResults( filenameBase, authorNetwork, authorList ):
    """ Print authorList and -network. """

    print( "saving authorlist")
    outfilename = filenameBase + extensionDefault_authorlist
    f = open( outfilename, "w")
    f.write( "author, papercount\n" )
    for authorID in authorList.keys():
        f.write( "%s,%i\n" %(authorID, authorList[authorID]["papercount"]) )
    f.close()
    
    print( "saving authornetwork")
    outfilename = filenameBase + extensionDefault_authorNetwork
    f = open( outfilename, "w")
    f.write( "source,target,weight\n" )
    for author in authorNetwork.keys():
        for coAuthor in authorNetwork[author].keys():
            f.write(author+","+coAuthor+","+str(authorNetwork[author][coAuthor])+'\n')
    f.close()
    print( "Done." )
    return

def main( bib_database ):
    # parse entries
    authorList = dict() # for number of papers for each author
    authorNetwork = dict() # for number of links between pairs of authors
    ignoredEntriesCount = 0 # entries in bib_database that did not have "author"-field
    for e in bib_database.entries:
        try:
            authorIDs = genAuthorIDs( e["author"].split(" and ") )
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
    
    # print results
    print( "# total entries: %i\n# ignored entries: %i"  %( len(bib_database.entries),ignoredEntriesCount ) )
    print( "# authors: %i" %len(authorNetwork.keys()) )
    printResults( 'TBD',authorNetwork, authorList )
    return


if __name__ == '__main__':
    if len(argv) < 2:
        print("Analyse co-authorships in bibtex-files.\n")
        print("Usage:\n\t%s BIBTEXFILENAME" %argv[0])
    else:
        # read file
        filename = argv[1]
        try:
            with open(filename) as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file,parser = bibtexparser.bparser.BibTexParser(common_strings=True))
            main( bib_database )
        except FileNotFoundError:
            print("File `%s` not found. Aborting." %filename)
