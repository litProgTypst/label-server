

# import argparse
import os
import signal
import sys
# import yaml

import logging
logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s')

from waitress import serve, wasyncore
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from labelServer.app import createDbApp, createBaseApp
from labelServer.config import ConfigManager

def sigtermHandler(signum, frame) :

  # simply call sys.exit as this will raise a SystemExit exception which
  # is then "handled" by Waitress and if we care, can be handled by our
  # app.

  # consider sending and waiting for a Blinker signal followed by an
  # ExitNow exception. This would provide a softer shutdown sequence.

  # try raising the more specific ExitNow exception defined by
  # waitress.wasyncore.... most of our application does not care... BUT
  # our database update/insert operations should be protected.

  raise wasyncore.ExitNow()

  sys.exit(0)

shutDownExceptions = (wasyncore.ExitNow, KeyboardInterrupt, SystemExit)

def cli() :

  signal.signal(signal.SIGTERM, sigtermHandler)

  # setup the command line arguments
  config = ConfigManager()
  config.loadConfig()
  config.checkInterface({
    'tags.databases.*.baseUrl' : {
      'msg' : 'All tag databases MUST specify the baseUrl'
    },
    'tags.databases.*.localPath' : {
      'msg' : 'All tag databases MUST specify the localPath'
    },
    'tags.webserver.title' : {
      'default' : 'LPiT Labels'
    },
    'tags.webserver.host' : {
      'default' : '127.0.0.1'
    },
    'tags.webserver.port' : {
      'default' : 8890
    }
  })

  dbApps = {}
  appTemplateFolder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates'
  )
  for dbName, dbConfig in config['tags.databases'].items() :
    mountPoint = f"/{dbConfig['baseUrl']}"
    theApp = createDbApp(dbName, dbConfig, config)
    theApp.template_folder = appTemplateFolder
    # If the user has specified their own logging level then use it
    flaskLogLevel = config['tags.webserver.flaskLogLevel']
    if flaskLogLevel :
      theApp.logger.setLevel(flaskLogLevel)
    # theApp.config["EXPLAIN_TEMPLATE_LOADING"] = True
    dbApps[mountPoint] = theApp

  baseApp = createBaseApp(config)
  # baseApp.config["EXPLAIN_TEMPLATE_LOADING"] = True
  baseApp.template_folder = appTemplateFolder

  app = DispatcherMiddleware(baseApp, dbApps)

  # Adjust the Waitress logging levels....
  waitressLogLevel = config['tags.webserver.waitressLogLevel']
  if waitressLogLevel :
    wLogger = logging.getLogger('waitress')
    wLogger.setLevel(waitressLogLevel)

  # start the Flask App using Waitress
  if not config['quiet'] :
    print("\nYour Waitress will serve you on:")
    print(f"  http://{config['tags.webserver.host']}:{config['tags.webserver.port']}")  # noqa
    print("")

  try :
    serve(
      app,
      host=config['tags.webserver.host'],
      port=config['tags.webserver.port'],
    )
  except shutDownExceptions :
    pass

  print("\nYour Waitress has left")

