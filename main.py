import bibtexparser
from bibtexparser.customization import *
from bibtexparser.latexenc import latex_to_unicode

filename = 'phd.bib'

with open(filename) as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file,parser = bibtexparser.bparser.BibTexParser(common_strings=True))

network=dict()
for e in bib_database.entries:
    try:
        list_authors=e["author"].split(" and ")
        for a in  range(len(list_authors)):
            for b in  range(a+1,len(list_authors)):
                auth_a=splitname(latex_to_unicode(list_authors[a]))
                auth_b=splitname(latex_to_unicode(list_authors[b]))
                author_a_id=(auth_a["last"][0]+auth_a["first"][0])
                author_b_id=(auth_b["last"][0]+auth_b["first"][0])
                if(author_a_id != author_b_id):
                    if(not(author_a_id in network.keys())):
                        network[author_a_id] = dict()
                    if(not(author_b_id in network[author_a_id])):
                        network[author_a_id][author_b_id]= 0
                    if(not(author_b_id in network.keys())):
                        network[author_b_id] = dict()
                    if(not(author_a_id in network[author_b_id])):
                        network[author_b_id][author_a_id]= 0
                    network[author_a_id][author_b_id] = network[author_a_id][author_b_id] + 1
                    network[author_b_id][author_a_id] = network[author_b_id][author_a_id] + 1
    except KeyError as e:
        # entry without 'author' are ignored
        print('KeyError %s, entry ignored.' %str(e))
        pass
    
print("source,target,weight")
for l in network.keys():
    for u in network[l].keys():
        print(l+","+u+","+str(network[l][u]))
