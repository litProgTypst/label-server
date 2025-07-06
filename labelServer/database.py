
import logging
import os
import sqlite3
import sys
# import yaml

def createDb() :
  if len(sys.argv) < 2 :
    print("""
usage: labelCreateDb <dbPath>

where <dbPath> is a (possibly non-existent) path to a SQLite3 database
    """)
    sys.exit(1)

  dbPath = sys.argv[1]
  print(f"Creating SQLite3 database: {dbPath}")

  with sqlite3.connect(dbPath) as con :
    cur = con.cursor()
    try :
      cur.execute("""
CREATE TABLE labels (
  tag INTEGER PRIMARY KEY AUTOINCREMENT,
  label TEXT,
  desc TEXT,
  inuse INTEGER DEFAULT 1
)
      """)
      cur.execute("CREATE UNIQUE INDEX labelindex ON labels(label)")
      cur.execute("CREATE VIRTUAL TABLE labelsfts USING FTS5(label, desc)")
    except Exception as err :
      print(f"Could not create the database {dbPath}")
      print(repr(err))

class LabelDatabase(object) :

  def __init__(self, dbName, dbConf) :
    self.dbName = dbName
    self.dbConf = dbConf
    self.log    = logging.getLogger(dbName)
    if 'logLevel' in dbConf :
      self.log.setLevel(dbConf['logLevel'])

    if 'localPath' not in self.dbConf :
      self.dbConf['localPath'] = f"{self.dbName}.sqlite"
    # newDB = False
    dbPath = self.dbConf['localPath']
    self.dbPath = dbPath
    self.log.info(f"Connecting to {dbPath}")
    if not os.path.isfile(dbPath) :
      self.log.critical(f"Could not find the {dbName} database ({dbPath})")
      self.log.critical(f"The {dbName} database MUST be created before running the webserver")  # noqa
      self.log.info(f"You can create the {dbName} database using the `lgtImporter` script")  # noqa
      sys.exit(1)

  def update(self, label, desc, inuse) :
    # print(label, desc, inuse)
    with sqlite3.connect(self.dbPath) as con :
      cur = con.cursor()
      try :
        cur.execute(
          "INSERT INTO labels (label, desc, inuse) VALUES(?,?,?)", (label, desc, inuse)  # noqa
        )
        cur.execute(
          "INSERT INTO labelsfts (label, desc) VALUES(?,?)", (label, desc)
        )
      except sqlite3.IntegrityError :
        cur.execute(
          f"UPDATE labels SET desc='{desc}', inuse='{inuse}' WHERE label = '{label}'"  # noqa
        )
        cur.execute(
          f"UPDATE labelsfts SET desc='{desc}' WHERE label = '{label}'"
        )

  def findLabel(self, label) :
    theRows = []
    with sqlite3.connect(self.dbPath) as con :
      res = con.cursor().execute(
        f"SELECT tag, label, desc, inuse FROM labels WHERE labels.label = '{label}'"  # noqa
      )
      for aRow in res :
        theRows.append({
          'tag'   : aRow[0],
          'label' : aRow[1],
          'desc'  : aRow[2],
          'inuse' : aRow[3]
        })
        break  # we only want the first one!
    return theRows

  def searchKeywords(self, searchQuery) :
    theRows = []
    with sqlite3.connect(self.dbPath) as con :
      # see: https://www.sqlitetutorial.net/sqlite-full-text-search/
      res = con.cursor().execute(
        f"SELECT label, desc FROM labelsfts WHERE labelsfts MATCH '{searchQuery}'"  # noqa
      )
      for aRow in res :
        theRows.append({
          'label'  : aRow[0],
          'desc'  : aRow[1],
        })
    return theRows
