#!/usr/bin/env python

import glob
import os
import sqlite3
import sys
import yaml

from lpilGerbyConfig.config import ConfigManager

def cli() :
  config = ConfigManager()
  config.loadConfig()
  config.checkInterface({
    'tags.localPath' : {
      'msg' : 'Can not collect tags database if no localPath specified'
    },
  })

  usedLabels = {}
  definedLabels = {}
  missingLabels = {}

  dbPath = config['tags.localPath']
  dbName = os.path.basename(dbPath).split('.')[0]
  with sqlite3.connect(dbPath) as db :
    dbCursor = db.cursor()
    rows = dbCursor.execute("SELECT * FROM labels")
    for aRow in rows :
      aLabel = aRow[1]
      definedLabels[aLabel] = True

  for aDocName in config['documents'].keys() :
    aDocPath = config[('documents', aDocName, 'dir')]
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

  labelsPath = f"{dbName}-labels.yaml"
  labelsPath = config['tags.labelsPath']
  if not labelsPath :
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
