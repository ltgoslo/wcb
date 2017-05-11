Wikipedia Corpus Builder
===
Wikipedia Corpus Builder is a toolkit for creating clean (i.e. most content that usually are of little use for most NLP and IR tasks is removed) corpora from database snapshots of Mediawiki powered wikis. The Corpus Builder was created by [Lars J. Solberg](https://github.com/larsjsol/wcb) for his [master thesis](https://www.duo.uio.no/handle/10852/34914) in 2012.

It is currently being updated and reworked in order to make it more usable for the public. 

[Old documentation](http://moin.delph-in.net/WcbTop)

### Table of Contents
* [Setup](#setup)
* [Script invocation](#script-invocation)

## Setup

_to-do, copy from http://moin.delph-in.net/WcbTop_

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

