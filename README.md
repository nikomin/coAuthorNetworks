Script to generate co-authorship network from bibtex file using python (so far doesn't work with python3).
The result will depend a lot of the quality of your bibliography (two slightly different orthograph will result in two different nodes)

The script uses [bibtexparser](https://github.com/sciunto-org/python-bibtexparser)
Quick install with pip:
```bash
pip2 install bibtexparser 
```


To use the script:
```bash
python2 main.py filename >  edgelistNames.csv
```

where `filenemane` is the name of of `.bib` file

You can then open the edgelist with your favorite network handler 

An example from my own PhD thesis is available in `example/`

![](example/phdNET.png)
