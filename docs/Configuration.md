# Configuration file formats

## Goal

We currently have a large number of configuration files. We really need
one or two.

## Solution

The following tools will each have their own (private) configuration files:

- PlasTeX (not in our control)
- lpilMagicRunner (none used)
- cmCapture
- VSCodium (not in our control)

The following tools will share their configuration files:

- lpilGerbyBuilder (nightly rebuild)
- lgtWebserver (tags/labels mapping webserver)
- lgtExplorer, ltgImporter (export/import tags/lables mappings)
- lgtScanner (check the current tags/labels mappings for omissions)
- gerbyRunner (PlasTeX/Gerby webserver)
- gerbyCompiler (database builder for gerbyRunner)

This shared configuration format will have the following structure:

- baseDir (all tools can over ride this on the command line)

- documents:
  - doc
  - gitUrl
  - dir

- tags:  (tags/labels mapping)
  - localPath
  - gitUrl (an external version controlled version of the mapping)
  - remotePath
  - databases (see below)
  - webServer (see below)

- gerby: (the gerbied version of the document(s) )
  - localPath
  - [gitUrl] (?)
  - remotePath
  - gerbyConfigurationConstants (see below)
  - compilerFlags (see below)
  - templatesDir
  - webServer (see below)

Both of the `tags` and `gerby` keys will contain their own version of the following:

- webServer:
  - host
  - port
  - baseUrl
  - title
  - logging
  - verbose
  - quiet

The databases key will contain:

- databases (dict; key is name of database
  - baseUrl
  - logLevel

The gerbyConfigurationConstants will contain:

-  COMMENTS
-  DATABASE
-  UNIT
-  DEPTH
-  PATH
-  PAUX
-  TAGS
-  PDF

The compilerFlag will contain:

- noTags
- noProofs
- noFootnotes
- noSearch
- noParts
- noInactivityCheck
- noDependencies
- noExtras
- noNames
- noBibliography
- noCitations
- noTagStats
- noBookStats

## Analysis

- PlasTex: A Python configuration file (TOML like) located in various
  locations including `~/.plastex` (not generally used -- silently ignored
  if it does not exist)

- PlasTeX LPiL plugin: `~/.config/cfdoit/config.yaml` (only really needed
  for the `buildDir` value)

- `lpilGerbyBuilder`: a YAML file which includes:

  - baseDir

  - `documents` (array) which are basically document repositories:
    - doc
    - gitUrl
    - dir

  - tagsDatabase:
    - localPath
    - gitUrl
    - remotePath

  - gerbyWebserver
    - localPath
    - remotePath
    - host
    - port
    - ...

- `lgtWebserver` a YAML file required.
  - webserver config
    - host
    - port
    - title
    - log levels
  - databases (external document catalogues (fingerPieces/diSimplex))
    - baseUrl
    - logLevel

- `lgtExporer`, `lgtImporter` : a YAML file but really we only need:
  - `baseDir`
  - `dbPath`
  - `tagsFile`
  - `labelsFile`

- `lgtScanner` : a YAML file which requires a list of `documents`
  directories:
  - `baseDir`
  - `documents` (array) which are basically document repositories:
    - dir
    - [doc]
    - [gitUrl]

- `lpilMagicRunner` no configuration file used.

- `gerbyRunner` a YAML file, required and not used by anything else:
  - gerby config
  - webserver config

- `gerbyCompiler`
  - `baseDir`
  - tagsDatabase:
    - localPath
    - [gitUrl]
    - [remotePath]
  - gerbyWebserver:
    - localPath
    - [remotePath]
    - [...]

- `cmCapture` unknown.... again not used by anything else...

- `VSCodium` required and not used by anything else, unchangeable.

**Questions**

**Q**: Can we amalgamate the `unattendedDSBuild` and `lgt*` configuration
       files?

**A**: Yes if we allow any of the tools which use the format to override
       the `baseDir` from the command line.
