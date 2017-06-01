Wikipedia Corpus Builder
===
Wikipedia Corpus Builder is a toolkit for creating clean (i.e. most content that usually are of little use for most NLP and IR tasks is removed) corpora from database snapshots of Mediawiki powered wikis. The Corpus Builder was created by [Lars J. Solberg](https://github.com/larsjsol/wcb) for his [master thesis](https://www.duo.uio.no/handle/10852/34914) in 2012.

It is currently being updated and reworked in order to make it more usable for the public. 

[Old documentation](http://moin.delph-in.net/WcbTop)

### Table of Contents
* [Setup](#setup)
* * [Installing dependencies](#installing-dependencies)
* * [Known issues](#known-issues)
* [Running on the English Wikipedia](#running-on-the-english-wikipedia)
* [Script invocation](#script-invocation)

## Setup

The project is built and tested on Python 2.7. if you're accustomed to another version or lacking access to install dependencies try [virtualenv](https://pypi.python.org/pypi/virtualenv).

**Dependencies:**  
- [mwlib](https://github.com/pediapress/mwlib)
- [mwlib.cdb 0.1.1](https://pypi.python.org/pypi/mwlib.cdb/0.1.1)
- [tokenizer](http://www.cis.uni-muenchen.de/~wastl/misc/) (has since been removed, and is included in the project)
- [srilm](http://www.speech.sri.com/projects/srilm/)

If the command `python -c 'from mwlib.cdb import cdbwiki'` does not give any error message and your shell is able to find `tokenizer` and `ngram` (from srilm) you should be in good shape.

### Installing Dependencies
```
pip install mwlib
pip install mwlib.cdb
```

#### Known Issues

##### (On OS X) fatal error: 'timelib_config.h' file not found (see [this issue](https://github.com/pediapress/timelib/issues/6)), solution:
1. `pip download timelib` which saves timelib zipped to your current folder
2. extract the zip-archive and edit setup.py:
```python
    # change the following
    ext_modules=[Extension("timelib", sources=sources,
                            libraries=libraries,
                            define_macros=[("HAVE_STRING_H", 1)])],
    # to this
    ext_modules=[Extension("timelib", sources=sources,
                            include_dirs=[".", "ext-date-lib"],
                            libraries=libraries,
                            define_macros=[("HAVE_STRING_H", 1)])],
```

## Running on the English Wikipedia
The project comes with pre-configuration for the following snapshots. 
- [2008-07-27]
- [2017-02-01] 

#### Using a pre-configured snapshot
1. Downlad the snapshot
2. Decompress: `bunzip enwiki-SNAPSHOT-pages-articles.xml.bz2`
3. Create a constant database: `mw-buildcdb --input enwiki-SNAPSHOT-pages-articles.xml --output OUTDIR`
4. Most of the WCB modules need access to a paths configuration file. They determine its location by examining the `PATHSFILE` environment variable, set it like so: `export PATHSFILE=./wcb/enwiki-SNAPSHOT/paths.txt` (in your ~/.bash_profile for persistence).

As a test run

## Script invocation

**- python build\_corpus.py** (builds a corpus for a dump or specified list of articles)
```
usage: build_corpus.py [-h] [--clean-port CLEAN_PORT]
                       [--dirty-port DIRTY_PORT] [--processes PROCESSES]
                       [--blacklist BLACKLIST]
                       [--article-list ARTICLE_LIST | --file-list FILE_LIST]
                       out_dir
```
**- python getMarkup.py** (gets the raw markup of an article)
```
usage: getMarkup.py [-h] article

```
**- python list\_articles.py** (lists article names)  

**-python printNodes.py** (Prints the syntax tree of an article)  
*Not Working due to an exception in nuwiki*

