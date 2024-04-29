#!/usr/bin/env python

import glob
import os
import sqlite3
import sys
import yaml

from lpilGerbyConfig.config import ConfigManager

def scanDatabase(chosenDocument, databaseConfig, collectionConfig) :
  usedLabels = {}
  definedLabels = {}
  missingLabels = {}

  dbPath = databaseConfig['localPath']
  dbName = os.path.basename(dbPath).split('.')[0]
  with sqlite3.connect(dbPath) as db :
    dbCursor = db.cursor()
    rows = dbCursor.execute("SELECT * FROM labels")
    for aRow in rows :
      aLabel = aRow[1]
      definedLabels[aLabel] = True

  for aDocName, aDocConfig in collectionConfig['documents'].items() :
    if chosenDocument and chosenDocument != aDocName.lower() : continue
    aDocPath = aDocConfig['dir']
    for aPath in glob.iglob(
      "**/*.aux", root_dir=aDocPath, recursive=True) :
      fullPath = os.path.join(aDocPath, aPath)
      with open(fullPath) as auxFile :
        for aLine in auxFile :
          if aLine.startswith("\\newlabel") :
            aLabel = aLine.split("{")[1].rstrip("}")
            usedLabels[aLabel] = True
            if aLabel not in definedLabels :
              if fullPath not in missingLabels :
                missingLabels[fullPath] = []
              missingLabels[fullPath].append(aLabel)

  if 'labelsPath' in databaseConfig :
    labelsPath = databaseConfig['labelsPath']
  else :
    labelsPath = dbPath.replace('.sqlite', '-labels')

  thePath = labelsPath+'-used.yaml'
  with open(thePath, 'w') as labelsFile :
    labelsFile.write(yaml.dump(sorted(usedLabels.keys())))
    labelsFile.write("\n")

  thePath = labelsPath+'-missing.yaml'
  with open(thePath, 'w') as labelsFile :
    labelsFile.write(yaml.dump(missingLabels))
    labelsFile.write("\n")

  thePath = labelsPath+'-defined.yaml'
  with open(thePath, 'w') as labelsFile :
    labelsFile.write(yaml.dump(sorted(definedLabels.keys())))
    labelsFile.write("\n")

def cli() :
  config = ConfigManager(
    chooseDatabase=True,
    chooseCollection=True,
    chooseDocument=True
  )
  config.loadConfig()
  config.checkInterface({
    'tags.databases.*.localPath' : {
      'msg' : 'Can not scan tags database if no localPath specified'
    },
    'gerby.collections.*.documents.*.dir' : {
      'msg' : 'Can not scan tags database if no document directories specified'
    },
  })

  for aDatabaseName, aDatabaseConfig in config['tags.databases'].items() :
    if config.cmdArgs['database'] and \
      config.cmdArgs['database'] != aDatabaseName.lower() : continue
    for aCollectionName, aCollectionConfig in config['gerby.collections'].items() :
      if config.cmdArgs['collection'] and \
        config.cmdArgs['collection'] != aCollectionName.lower() : continue
      if aDatabaseName.lower() == aCollectionName.lower() :
        scanDatabase(
          config.cmdArgs['document'], aDatabaseConfig, aCollectionConfig
        )
