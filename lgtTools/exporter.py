#!/usr/bin/env python

import csv
import os
import sqlite3
import sys
import yaml

from lpilGerbyConfig.config import ConfigManager

# see: https://stackoverflow.com/a/1181922
alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def exportDatabase(databaseConfig) :
  dbPath = databaseConfig['localPath']
  dbName = os.path.basename(dbPath).split('.')[0]

  if 'tagsPath' in databaseConfig :
    tagsPath = databaseConfig['tagsPath']
  else :
    tagsPath = dbPath.replace('.sqlite', '.tags')

  tagsFile = open(tagsPath, "w")

  if 'labelsPath' in databaseConfig :
    labelsPath = config['labelsPath']
  else :
    labelsPath = dbPath.replace('.sqlite', '.labels')

  labelsFile = open(labelsPath, "w", newline='')
  labelsWriter = csv.writer(labelsFile, quoting=csv.QUOTE_ALL)

  db = sqlite3.connect(dbPath)
  dbCursor = db.cursor()

  rows = dbCursor.execute("SELECT * FROM labels ORDER BY tag ASC")
  for aRow in rows:
    labelsWriter.writerow(aRow)
    tagsFile.write(f"{int2tag(aRow[0])},{aRow[1]}\n")

  db.close()
  labelsFile.close()
  tagsFile.close()

def int2tag(tagInt) :
  tagStr = ''
  while tagInt != 0 :
    tagInt, i = divmod(tagInt, 36)
    tagStr = alphabet[i] + tagStr
  while len(tagStr) < 4 :
    tagStr = '0' + tagStr
  return tagStr

def cli() :
  config = ConfigManager(chooseDatabase=True)
  config.loadConfig()
  config.checkInterface({
    'tags.databases.*.localPath' : {
      'msg' : 'Can not collect tags database if no localPath specified'
    },
  })

  for aDatabaseName, aDatabase in config['tags.databases'].items() :
    if config.cmdArgs['database'] and \
      config.cmdArgs['database'] != aDatabaseName.lower() : continue
    exportDatabase(aDatabase)