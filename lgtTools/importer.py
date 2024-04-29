#!/usr/bin/env python

import csv
import os
import sqlite3
import sys
import yaml

from lpilGerbyConfig.config import ConfigManager

def importDatabase(databaseConfig) :
  dbPath = databaseConfig['localPath']
  dbName = os.path.basename(dbPath).split('.')[0]

  if 'labelsPath' in databaseConfig :
    labelsPath = databaseConfig['labelsPath']
  else :
    labelsPath = dbPath.replace('.sqlite', '.labels')

  if os.path.isfile(dbPath) :
    print(f"\nThe labels SQLite3 database [{dbPath}] exists!")
    print("\nAre you sure you want ot re-create it?")
    print("\nType Ctl-C to abort or return to continue:")
    input()
    print(f"Removing [{dbPath}]")
    os.remove(dbPath)

  print(f"Creating a new database [{dbPath}]")
  db = sqlite3.connect(dbPath)
  dbCursor = db.cursor()

  # Create the main labels table. This table contains the definitive
  # tag->label mapping

  dbCursor.execute("""
CREATE TABLE labels (
  tag INTEGER PRIMARY KEY AUTOINCREMENT,
  label TEXT,
  desc TEXT,
  inuse INTEGER DEFAULT 1
)
""")

  dbCursor.execute(
    "CREATE UNIQUE INDEX labelindex ON labels(label)"
  )

  # Create the FTS5 full text searh "index"
  # see: https://www.sqlitetutorial.net/sqlite-full-text-search/

  dbCursor.execute(
    "CREATE VIRTUAL TABLE labelsfts USING FTS5(label, desc)"
  )

  if not os.path.isfile(labelsPath) :
    print(f"We have created an empty database...")
  else :
    try :
      with open(labelsPath, "r", newline='') as labelsFile :
        labelsReader = csv.reader(labelsFile)
        for aRow in labelsReader :
          print(yaml.dump(aRow))
          dbCursor.execute(
            "INSERT INTO labels (tag, label, desc, inuse) VALUES(?,?,?,?)", aRow
          )
          dbCursor.execute(
            "INSERT INTO labelsfts (label, desc) VALUES(?,?)",
            (aRow[1], aRow[2])
          )
        db.commit()
    except Exception as err:
      print(repr(err))
      print(f"Could not open the labels CSV file [{labelsPath}]")
      print(f"We have created an empty database...")
  db.close()

def cli() :
  config = ConfigManager(chooseDatabase=True)
  config.loadConfig()
  config.checkInterface({
    'tags.databases.*.localPath' : {
      'msg' : 'Can not import tags database if no localPath specified'
    },
  })

  for aDatabaseName, aDatabase in config['tags.databases'].items() :
    if config.cmdArgs['database'] and \
      config.cmdArgs['database'] != aDatabaseName.lower() : continue
    importDatabase(aDatabase)