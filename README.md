Wikipedia Corpus Builder
===
Wikipedia Corpus Builder is a toolkit for creating clean (i.e. most content that usually are of little use for most NLP and IR tasks is removed) corpora from database snapshots of Mediawiki powered wikis. The Corpus Builder was created by [Lars J. Solberg](https://github.com/larsjsol/wcb) for his [master thesis](https://www.duo.uio.no/handle/10852/34914) in 2012.

It is currently being updated and reworked in order to make it more usable for the public. 

[Old documentation](http://moin.delph-in.net/WcbTop)

### Table of Contents
* [Setup](#setup)
* * [Dependencies](#dependencies)
* * [Known issues](#known-issues)
* [Running on the English Wikipedia](#running-on-the-english-wikipedia)
* [Script invocation](#script-invocation)

## Setup

The project is built and tested using Python 2.7. if you're accustomed to another version or lacking access to install dependencies try [virtualenv](https://pypi.python.org/pypi/virtualenv).

You should have about 90GB of free space to download and parse a recent English Wikipedia dump:
- ~60GB for extracting the downloaded snapshot (which is ~13GB)
- ~20GB for the constant database built with mwlib
- ~5GB for the parsed text generated by WCB


### Dependencies
- [mwlib](https://github.com/pediapress/mwlib)
- [mwlib.cdb 0.1.1](https://pypi.python.org/pypi/mwlib.cdb/0.1.1)
- [tokenizer](http://www.cis.uni-muenchen.de/~wastl/misc/) (has been removed from the link, and it's included in the project)
- [srilm](http://www.speech.sri.com/projects/srilm/)

**Installation:**  
- `pip install mwlib`
- `pip install mwlib.cdb`
- [Download and install sirlm using the instructions here](http://www.speech.sri.com/projects/srilm/download.html)
- Installing tokenizer:  
- 1. `cd /path-to-wcb/libs/tokenizer`
- 2. `./configure --prefix=/path-to-wcb/libs/tokenizer/build` 
- 3. `make && make install`
- 4. The executable `tokenizer` should now be in `/path-to-wcb/libs/tokenizer/build/bin`

Finally, copy `tokenizer` and `ngram` (from srilm) to `/usr/local/bin` or another path that is accessible from your shell.  
If the command `python -c 'from mwlib.cdb import cdbwiki'` does not give any error message and your shell is able to find `tokenizer` and `ngram` (from srilm) you should be in good shape.

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
- [2008-07-27](missing-link)
- [2017-02-01 (57GB)](missing-link)

#### Using a pre-configured snapshot
1. Downlad the snapshot
2. Decompress: `bunzip enwiki-SNAPSHOT-pages-articles.xml.bz2`
3. Create a constant database: `mw-buildcdb --input enwiki-SNAPSHOT-pages-articles.xml --output OUTDIR`
4. Change the `wikiconf` entry in `/wcb/enwiki-SNAPSOT/paths.txt` to point to the `wikiconf.txt` file generated in the previous step.
5. The WCB modules in this project need access to the `paths.txt` configuration file. They determine its location by examining the `PATHSFILE` environment variable, set it like so: `export PATHSFILE=./wcb/enwiki-SNAPSHOT/paths.txt` (in your ~/.bash_profile for persistence).

#### Configuring a new dump
1. Downlad the snapshot
2. Decompress: `bunzip enwiki-SNAPSHOT-pages-articles.xml.bz2`
3. Create a constant database: `mw-buildcdb --input enwiki-SNAPSHOT-pages-articles.xml --output OUTDIR`
4. Now you have to add configuration for a new snapshot. Copy the `enwiki-20170201` directory to a new directory reflecting your snapshot's date.
5. Change the `wikiconf` entry in `/wcb/enwiki-SNAPSOT/paths.txt` to point to the `wikiconf.txt` file generated in step 3.
6. The WCB modules in this project need access to the `paths.txt` configuration file. They determine its location by examining the `PATHSFILE` environment variable, set it like so: `export PATHSFILE=./wcb/enwiki-SNAPSHOT/paths.txt` (in your ~/.bash_profile for persistence).

#### Test run
To test the configuration, try running the corpus builder on the list of test articles, like so:

```
mkdir test-dir
./wcb/scripts/build_corpus.py --articles-list /wcb/test-articles.txt test-dir
```

The first invocation of this command will take some time as it will examine all the templates in the snapshot.

#### Full run
```
mkdir out-dir
./wcb/scripts/build_corpus.py -p NUMBER_OF_PROCESSES out-dir
```

#### Adding support for additional languages
*In progress...*

## Script invocation

**- python build\_corpus.py** (builds a corpus for a complete dump or specified list of articles)
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

