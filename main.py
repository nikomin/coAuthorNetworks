"""
Analysis of co-authorships between publications taken from a bibtex file.
"""
import bibtexparser
from bibtexparser.customization import splitname
from bibtexparser.latexenc import latex_to_unicode

filename = 'phd.bib'

with open(filename) as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file,parser = bibtexparser.bparser.BibTexParser(common_strings=True))



def genAuthorID(authorName):
    """ Return a unique ID given an authorName. """
    fullName = splitname(latex_to_unicode(authorName))
    return fullName["last"][0]+fullName["first"][0]
    
authorList=dict()
authorNetwork=dict()
ignoredEntriesCount = 0
for e in bib_database.entries:
    try:
        list_authors=e["author"].split(" and ")
        authorIDs = []
        for authorName in list_authors:
            authorIDs.append( genAuthorID(authorName) )

        for i, author_a_id in enumerate(authorIDs):
            if not( author_a_id in authorList.keys() ):
                authorList[ author_a_id ] = {'papercount': 0}
            authorList[ author_a_id ]['papercount'] += 1
            for j, author_b_id in  enumerate(authorIDs[i+1:]):
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
    except KeyError as e:
        # entries without 'author' are ignored
        ignoredEntriesCount += 1
        pass

    

print( "# total entries: %i\n# ignored entries: %i"  %( len(bib_database.entries),ignoredEntriesCount ) )
print( "# authors: %i" %len(authorNetwork.keys()) )

print( "======================================================================")
print( "author, papercount" )
for authorID in authorList.keys():
    print( "%s,%i" %(authorID, authorList[authorID]["papercount"]) )

print( "======================================================================")
print( "source,target,weight" )

for author in authorNetwork.keys():
    for coAuthor in authorNetwork[author].keys():
        print(author+","+coAuthor+","+str(authorNetwork[author][coAuthor]))
