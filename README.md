# Co-authorship analysis

This software to help analyse the literature of your research. Which papers share
authors, who published with whom? The analysis should work with any
bibtex-file. The cleaner the bibtex-file (no duplicate entries,
identical author name spellings, etc.) the more precise the output
will be.

It is not intended for the scientific analysis of publications.

The code is based on the original ideas by Simon Carrignon, as it is hosted
[here](https://framagit.org/sc/pybibnet).

## Prerequisites

The software is developed and used with `python3`. It makes use of the
package
[`bibtexparser`](https://github.com/sciunto-org/python-bibtexparser),
which can be installed with 

    pip install bibtexparser

## Usage

```bash
./main.py >  edgelistNames.csv
```

