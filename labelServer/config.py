
# command line arguments consist of an unknown number of paths...

# paths that end with '.yaml' will be loaded and merged into the
# configuration (any instance of '$baseDir' being replaced with the
# current value of 'baseDir')

# paths that do not end with '.yaml' are assumed to be the current value
# of 'baseDir'

import argparse
import copy
import os
import yaml

# List the known Gerby Constants so that IF they are in the TOML file
# they will be used to over-ride the computed values
gerbyConsts = [
  "COMMENTS",
  "DATABASE",
  "UNIT",
  "DEPTH",
  "PATH",
  "PAUX",
  "TAGS",
  "PDF"
]

def mergeYamlData(yamlData, newYamlData, thePath, baseDir) :
  """ This is a generic Python merge. It is a *deep* merge and handles
  recursive dictionary structures """

  # check to ensure both the yamlData and newYamlData are consistent.
  if type(yamlData) is None :
    print("ERROR(mergeYamlData): yamlData should NEVER be None ")
    print(f"ERROR(megeYamlData): Stopped merge at {thePath}")
    return

  if type(yamlData) != type(newYamlData) :  # noqa
    print(f"ERROR(mergeYamlData): Incompatible types {type(yamlData)} and {type(newYamlData)} while trying to merge YAML data at {thePath}")  # noqa
    print(f"ERROR(mergeYamlData): Stopped merge at {thePath}")
    return

  # implement a recusrive definition of the baseDir
  if 'baseDir' in newYamlData :
    baseDir = newYamlData['baseDir'].replace('$baseDir', baseDir)
    newYamlData['baseDir'] = baseDir

  # perform the merge at the same time expanding any '~' and '$baseDir' in
  # paths (strings).
  if type(newYamlData) is dict :
    for key, value in newYamlData.items() :
      if isinstance(value, str) :
        value = value.replace('$baseDir', baseDir)
        if value.startswith('~') :
          value = os.path.expanduser(value)
        yamlData[key] = value
      elif isinstance(value, dict) :
        if key not in yamlData :
          yamlData[key] = {}
        mergeYamlData(yamlData[key], value, thePath + '.' + key, baseDir)
      else :
        yamlData[key] = copy.deepcopy(value)
  else :
    print("ERROR(mergeYamlData): YamlData MUST be a dictionary.")
    print(f"ERROR(mergeYamlData): Stopped merge at {thePath}")
    return

class ConfigManager(object) :

  def __init__(
    self,
    addArgsFunc=None,
    chooseCollection=False,
    chooseDatabase=False,
    chooseDocument=False,
  ) :
    self.data = {}

    # setup the command line arguments
    parser = argparse.ArgumentParser()
    if addArgsFunc : addArgsFunc(parser)
    parser.add_argument(
      'configPaths', nargs='+',
      help="One or more paths to either the current 'base directory' or YAML configuration files which collectively describe how to configure this LPiL Gerby tool. (YAML files MUST have the extension '.yaml')"  # noqa
    )
    if chooseCollection :
      parser.add_argument(
        '--collection',
        help="Only work on this collection"
      )
    if chooseDatabase :
      parser.add_argument(
        '--database',
        help="Only work on this database"
      )
    if chooseDocument :
      parser.add_argument(
        '--document',
        help="Only work on this document"
      )
    parser.add_argument(
      '-v', '--verbose', action='store_true', default=False,
      help="Be verbose [False]"
    )
    parser.add_argument(
      '-q', '--quiet', action='store_true', default=False,
      help="Be quiet [False]"
    )

    self.cmdArgs = vars(parser.parse_args())
    if chooseCollection and self.cmdArgs['collection'] :
      self.cmdArgs['collection'] = self.cmdArgs['collection'].lower()
    if chooseDatabase and self.cmdArgs['database'] :
      self.cmdArgs['database'] = self.cmdArgs['database'].lower()
    if chooseDocument and self.cmdArgs['document'] :
      self.cmdArgs['document'] = self.cmdArgs['document'].lower()

    self.configPaths = []
    self.baseDirs = []

    for aConfigPath in self.cmdArgs['configPaths'] :

      if aConfigPath.startswith('~') :
        aConfigPath = os.path.abspath(
          os.path.expanduser(self.baseDir)
        )
      self.configPaths.append(aConfigPath)

  def _checkAKeyPath(self, theStrKeyPath, theKeyPath, theDef, theDict) :
    if not isinstance(theDict, dict) :
      raise KeyError(f"{theStrKeyPath} at {theKeyPath} is not a dictionary")
    theKey = theKeyPath.pop(0)
    if len(theKeyPath) < 1 :
      if theKey not in theDict :
        if 'default' in theDef : theDict[theKey] = theDef['default']
        elif 'msg' in theDef   : raise KeyError(
          f"{theStrKeyPath}: Could not find key [{theKey}]: {theDef['msg']} (b)"  # noqa
        )
        else : raise KeyError(f"{theStrKeyPath}: Could not find [{theKey}]")
      return

    if '*' == theKey :
      keys = list(theDict.keys())
    else :
      keys = [ theKey ]

    origDict    = theDict
    origKeyPath = theKeyPath

    for aKey in keys :
      theDict    = copy.copy(origDict)
      theKeyPath = copy.copy(origKeyPath)

      curStrKeyPath = theStrKeyPath
      if '*' == theKey :
        curStrKeyPath = theStrKeyPath.replace('*', aKey, 1)
      if aKey not in theDict :
        if 'msg' in theDef :
          raise KeyError(
            f"{theStrKeyPath}: Could not find key [{curStrKeyPath}]: {theDef['msg']} (a)"  # noqa
          )
        theDict[aKey] = {}
      theDict = theDict[aKey]
      self._checkAKeyPath(
        curStrKeyPath, theKeyPath, theDef, theDict
      )

  def checkInterface(self, keyList) :
    for theKeyPath, theDef in keyList.items() :
      if isinstance(theKeyPath, str) :
        theKeyPath = theKeyPath.split('.')
      theDict = self.data
      self._checkAKeyPath(
        '.'.join(theKeyPath), theKeyPath, theDef, theDict
      )

  def __getitem__(self, key, default=None) :
    if isinstance(key, (list, tuple)) : key = '.'.join(key)
    # origKey = key
    thePath = key
    theDict = self.data
    while '.' in thePath :
      key, thePath = thePath.split('.', maxsplit=1)
      if key not in theDict :
        return default
      theDict = theDict[key]
    if thePath not in theDict :
      return default
    return theDict[thePath]

  def __setitem__(self, key, value) :
    if isinstance(key, (list, tuple)) : key = '.'.join(key)
    thePath = key
    theDict = self.data
    while '.' in thePath :
      key, thePath = thePath.split('.', maxsplit=1)
      if key not in theDict :
        theDict[key] = {}
      theDict = theDict[key]

    theDict[thePath] = value

  def showConfig(self) :
    print(yaml.dump(self.data))

  def loadConfig(self) :
    baseDir = os.path.expanduser('~')

    config = {}
    yamlConfig = {}
    for aConfigPath in self.configPaths :

      if not aConfigPath.lower().endswith('.yaml') :
        baseDir = aConfigPath
        self.baseDirs.append(aConfigPath)
        continue

      try:
        with open(aConfigPath, 'rb') as yamlFile :
          yamlConfig = yaml.safe_load(yamlFile.read())
      except Exception as err :
        print(f"Could not load configuration from [{aConfigPath}]")
        print(repr(err))

    if yamlConfig :
      if 'baseDir' in yamlConfig :
        if len(self.baseDirs) < 1 :
          baseDir = yamlConfig['baseDir']
        del yamlConfig['baseDir']
      mergeYamlData(config, yamlConfig, '', baseDir)

    config['verbose'] = self.cmdArgs['verbose']

    config['configPaths'] = self.configPaths
    config['baseDirs'] = self.baseDirs

    # report the configuration if verbose
    if config['verbose'] :
      print(f"Loaded configuration from: [{self.configPaths}]\n")
      print("----- command line arguments -----")
      print(yaml.dump(self.cmdArgs))
      print("---------- configuration ---------")
      print(yaml.dump(config))

    self.data = config
