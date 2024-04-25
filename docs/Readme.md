# Design of the LPiL Gerby tagger tools

## Goal

We need to maintain a *global* database mapping Gerby tags to LaTeX
labels.

It would be useful if this *global* database could be maintained using a
web-based front end.

## Solution

### Webserver

See the sister repository
[lpil-gerby-tag-server](https://github.com/litProgLaTeX/lpil-gerby-tag-server)

### Utility scripts

We have a number of very simple (sqlite3) based scripts which, using one
of the mapping databases, can:

- **create and import** an existing CSV file (as exported below) into a
  mapping database

- **export** the database to both a tags and CSV file (The CSV file can be
  version controlled)

- **scan** the database and specified documents for all LaTeX labels which
  are:
    - missing
    - used
    - defined

## Problems

1. We want to use the *single* *global* tags database across *multiple*
   LPiL LaTeX documents. We can do this using the Gerby PlasTeX plugin's
   `--tags` option, by specifying a global location for the tags database.

2. We may want to run the PlasTeX/Gerby tool on a machine remote from
   where the Terminolgue webserver is hosted. This means we will need to get
   the Terminologue SQLite database from the remote server for local use.
   We assume we can do this by using `rsync`.

3. We need a "base" (short) LaTeX label for each LPiL LaTeX document.
   These base label tags will by convention be used as the *prefix* to
   all tags (initially) associated to this LPiL LaTeX document. This base
   tag will also provide a simple description of the intent of each LPiL
   LaTeX document.

3. We need to extract the required tag->LaTeX-label mapping from the
   lgtWebserver SQLite database.

4. We need a simple tool to scan the collection of LPiL-documents for
   missing reference tags.

## Other considerations

1. We need to maintain a LaTeX document inventory, which should include:

     - directory information
     - short-code (2-3 characters) used in page numbers(?)
     - (computed?) chapter number
     - footnote assignment(?)
     - image number assignment(?)

  This will be kept in a (small?) YAML configuration file.

