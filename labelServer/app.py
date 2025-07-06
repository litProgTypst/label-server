# import yaml

from flask import Flask, render_template, request, redirect
from labelServer.database import LabelDatabase

def createBaseApp(config) :
  app = Flask(__name__)

  @app.route("/")
  def hello() :
    return render_template("baseApp.html", config=config )

  return app

def createDbApp(dbName, dbConfig, config) :

  app = Flask(dbName)
  db  = LabelDatabase(dbName, dbConfig)

  def urlFor(aPath) :
    return f"/{dbConfig['baseUrl']}/{aPath}"

  def redirectTo(aPath) :
    return redirect(urlFor(aPath))

  def labelForm(labelValues) :
    return render_template(
      "labelForm.html",
      name=dbName,
      config=config,
      dbConf=dbConfig,
      labelValues=labelValues
    )

  def findLabelForm(findValues) :
    return render_template(
      "findLabelForm.html",
      name=dbName,
      config=config,
      dbConf=dbConfig,
      findValues=findValues
    )

  def keywordSearchForm(searchValues) :
    return render_template(
      "keywordSearchForm.html",
      name=dbName,
      config=config,
      dbConf=dbConfig,
      searchValues=searchValues
    )

  @app.get("/")
  def keywordSearchForm_get() :
    return keywordSearchForm({
      'label'  : '',
    })

  @app.post("/")
  def keywordSearchForm_post() :
    formData = request.form.to_dict()
    if not formData['keywords'] : return redirectTo("/")
    results  = db.searchKeywords(formData['keywords'])
    # print(yaml.dump(results))
    return render_template(
      "keywordSearchResults.html",
      name=dbName,
      config=config,
      dbConf=dbConfig,
      keywords=formData['keywords'],
      results=results
    )

  @app.get("/find")
  def findLabelForm_get() :
    return findLabelForm({
      'label' : ''
    })

  @app.get("/find/<aLabel>")
  def findLabel_get(aLabel=None) :
    if not aLabel : return redirectTo("/")
    return redirectTo(f"edit/{aLabel}")

  @app.post("/find")
  def findLabelForm_post() :
    formData = request.form.to_dict()
    return redirectTo(f"edit/{formData['label']}")

  @app.get("/new")
  def newLabelForm_get() :
    return labelForm({
      'label'  : '',
      'desc'   : '',
      'inuse'  : 1,
      'action' : 'new'
    })

  @app.get("/new/<aLabel>")
  def newLabeledForm_get(aLabel=None) :
    if not aLabel : return redirectTo("new")
    return redirectTo(f"edit/{aLabel}")

  @app.get("/edit/<aLabel>")
  def editLabelForm_get(aLabel=None) :
    if not aLabel : return redirectTo("/")
    results = db.findLabel(aLabel)
    if not results : results = [{ 'label' : aLabel, 'desc' : '', 'inuse' : 1 }]
    # print(yaml.dump(results[0]))
    return labelForm({
      'label'  : results[0]['label'],
      'desc'   : results[0]['desc'],
      'inuse'  : results[0]['inuse'],
      'action' : 'edit'
    })

  @app.post("/new")
  def newLabelForm_post() :
    formData = request.form.to_dict()
    inuse = 0
    if 'inuse' in formData : inuse = 1
    db.update(formData['label'], formData['desc'], inuse)
    return redirectTo("new")

  return app
