import bibtexparser
from bibtexparser.customization import *
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
        for a in  range(len(list_authors)):
            author_a_id=genAuthorID(list_authors[a])
            if not( author_a_id in authorList.keys() ):
                authorList[ author_a_id ] =  {'papercount': 0}
            authorList[ author_a_id ]['papercount'] += 1
            for b in  range(a+1,len(list_authors)):
                author_b_id=genAuthorID(list_authors[b])
                if(author_a_id != author_b_id):
                    if(not(author_a_id in authorNetwork.keys())):
                        authorNetwork[author_a_id] = dict()
                    if(not(author_b_id in authorNetwork[author_a_id])):
                        authorNetwork[author_a_id][author_b_id]= 0
                    if(not(author_b_id in authorNetwork.keys())):
                        authorNetwork[author_b_id] = dict()
                    if(not(author_a_id in authorNetwork[author_b_id])):
                        authorNetwork[author_b_id][author_a_id]= 0
                    authorNetwork[author_a_id][author_b_id] = authorNetwork[author_a_id][author_b_id] + 1
                    authorNetwork[author_b_id][author_a_id] = authorNetwork[author_b_id][author_a_id] + 1
    except KeyError as e:
        # entry without 'author' are ignored
        print('EE: KeyError %s, entry ignored.' %str(e))
        ignoredEntriesCount += 1
        pass

    

print( "# entries: %i , # ignored entries: %i"  %( len(bib_database.entries),ignoredEntriesCount ) )
print( "# authors: %i" %len(authorNetwork.keys()) )

print( "author, papercount" )
for authorID in authorList.keys():
    print( "%s,%i" %(authorID, authorList[authorID]["papercount"]) )

print( "source,target,weight" )

for author in authorNetwork.keys():
    for coAuthor in authorNetwork[author].keys():
        print(author+","+coAuthor+","+str(authorNetwork[author][coAuthor]))
