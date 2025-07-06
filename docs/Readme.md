# Design of the LPiT Label Server and Tools

## Goal

We need to maintain a *global* database managing Typst labels across a
collection of documents.

It would be useful if this *global* database could be maintained using a
web-based front end.

## Solution

### Webserver

This repository contains a very simple Flask/SQLite3 based web server to
allow the document writers to maintain and *describe* the Typst labels
used in a collection of documents.

This web server can maintain multiple collections of labels. Each
collection of labels is kept in its own SQLite3 database.

Associated with each unique label is an optional textual description as
well as a Boolean indicating whether or not the label is currently in use.

### Utility scripts

See the sister repository
[lpil-gerby-tag-tools](https://github.com/litProgLaTeX/lpil-gerby-tag-tools)

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

