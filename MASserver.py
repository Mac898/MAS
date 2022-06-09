# ©Macauley Lim 2021 -- File Licensed Under The GNU GPLv3. See The Full Notice In License.md For Binding Terms.
import logging, subprocess, time, os, re, random, json
from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified
import MASsettings

app = Flask(__name__)
app.config['SQLALCHEMY_TIMEOUT'] = "60"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://$$$$:$$$$@$$$$/SciEx?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

session = db.session

settings = MASsettings.Settings()
instanceLimit_Locations = settings.read("EXPERIMENT.RUNS_PER_LOCATION")
stimulilimitraw = settings.read("EXPERIMENT.RUNS_PER_STIMULUS")
regionfile = open("regions.json")
regions = json.load(regionfile)
locationslength = len(regions)
instanceLimit_Stimuli = stimulilimitraw * locationslength * instanceLimit_Locations
print(str(instanceLimit_Stimuli))
COMMAND_LIST = settings.read("SETTINGS.COMMANDORDER")

class VPN_LOCATIONS(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    VPN_LOCATION = db.Column(db.String(150), nullable=False)
    INSTANCES = db.Column(db.Integer)

class STIMULI(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    STIMULUS = db.Column(db.String(150), nullable=False)
    INSTANCES = db.Column(db.Integer)

class NODES(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    VPN_LOCATION = db.Column(db.String(150))
    STIMULUS = db.Column(db.String(150))
    ERRORS = db.Column(db.Text)
    COMMAND_LIST = db.Column(db.String(400))

class RESULTS(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    RESULT = db.Column(db.Text)
    STIMULUS = db.Column(db.String(150))
    LOCATION = db.Column(db.String(150))

class dbMigrations():
    def createDB():
        db.create_all()
        session.commit()
    def createLocation(location):
        locationobj = VPN_LOCATIONS(VPN_LOCATION=location, INSTANCES=0)
        session.add(locationobj)
        session.commit()
    def createStimulus(stimulus):
        stimulusobj = STIMULI(STIMULUS=stimulus, INSTANCES=0)
        session.add(stimulusobj)
        session.commit()
    def deleteDB():
        db.drop_all()
    def resetStimuliToTemplate():
        session.query(STIMULI).delete()
        stimuliCurrentTemplate = settings.read("EXPERIMENT.STIMULI_TEMPLATE")
        for item in stimuliCurrentTemplate:
            a = STIMULI(STIMULUS = str(item), INSTANCES=0)
            session.add(a)
        session.commit()
    def resetVPNLocationsToTemplate():
        session.query(VPN_LOCATIONS).delete()
        regionfile = open("regions.json")
        regions = json.load(regionfile)
        for item in regions:
            a = VPN_LOCATIONS(VPN_LOCATION = str(item), INSTANCES=0)
            session.add(a)
        session.commit()
    def resetInstanceCount():
        stimulus = session.query(STIMULI).all()
        for item in stimulus:
            item.INSTANCES = 0
            session.add(item)
        locations = session.query(VPN_LOCATIONS).all()
        for item in locations:
            item.INSTANCES = 0
            session.add(item)
        session.commit()

#admin routes
@app.route("/admin/createDB")
def handleAdminNewDB():
    dbMigrations.createDB()
    dbMigrations.resetStimuliToTemplate()
    dbMigrations.resetVPNLocationsToTemplate()
    dbMigrations.resetInstanceCount()
    return "OK"

@app.route("/admin/createLocation", methods=['POST'])
def handleAdminNewLocation():
    dbMigrations.createLocation(request.get_data().decode('utf-8'))
    return "OK"

@app.route("/admin/createStimulus", methods=['POST'])
def handleAdminNewStimulus():
    dbMigrations.createStimulus(request.get_data().decode('utf-8'))
    return "OK"

@app.route("/admin/deleteDB")
def handleAdminDeleteDB():
    dbMigrations.deleteDB()
    return "OK"

@app.route("/admin/resetStimuliToTemplate")
def handleAdminResetStimuliToTemplate():
    dbMigrations.resetStimuliToTemplate()
    return "OK"

@app.route("/admin/resetVPNLocationsToTemplate")
def handleAdminResetVPNToTemplate():
    dbMigrations.resetVPNLocationsToTemplate()
    return "OK"

@app.route("/admin/resetInstanceCount")
def handleAdminDeleteResetInstanceCount():
    dbMigrations.resetInstanceCount()
    return "OK"

#MASexsi routes


#MASclient routes
@app.route("/node")
def handleNewNode():
    vpn_locations = session.query(VPN_LOCATIONS).all()
    location = ""
    while True:
        location = random.choice(vpn_locations)
        if location.INSTANCES < instanceLimit_Locations:
            location.INSTANCES = location.INSTANCES + 1
            session.add(location)
            session.commit()
            location = location.VPN_LOCATION
            break
    stimuli = session.query(STIMULI).all()
    stimulus = ""
    while True:
        stimulus = random.choice(stimuli)
        if stimulus.INSTANCES < instanceLimit_Stimuli:
            stimulus.INSTANCES = stimulus.INSTANCES + 1
            session.add(stimulus)
            session.commit()
            stimulus = stimulus.STIMULUS
            break
    nodeCommand_List = COMMAND_LIST
    nodedbi = NODES(VPN_LOCATION = location, STIMULUS = stimulus, ERRORS = "", COMMAND_LIST = nodeCommand_List)
    session.add(nodedbi)
    session.commit()
    nodeid = nodedbi.id
    return str(nodeid)

@app.route("/results", methods=["POST"])
def handleSentResults():
    nodeid = request.headers.get("X-NODE-ID")
    result = request.get_data().decode('utf-8')
    nodedetails = session.query(NODES).filter(NODES.id == nodeid).first()
    stimulus = nodedetails.STIMULUS
    location = nodedetails.VPN_LOCATION
    dbobj = RESULTS(id = nodeid, RESULT = result, STIMULUS = stimulus, LOCATION = location)
    session.add(dbobj)
    session.commit()
    return "OK"

@app.route("/aptpackages")
def handleGetPackagesApt():
    rtext = ",".join(settings.read("SETTINGS.VM.APTPACKAGES"))
    response = make_response(rtext, 200)
    response.mimetype = "text/plain"
    return response

@app.route("/pippackages")
def handleGetPackagesPip():
    rtext = ",".join(settings.read("SETTINGS.VM.PIPPACKAGES"))
    response = make_response(rtext, 200)
    response.mimetype = "text/plain"
    return response

@app.route("/error", methods=["POST"])
def handleError():
    nodeid = request.headers.get("X-NODE-ID")
    nodedetails = session.query(NODES).filter(NODES.id == nodeid).first()
    nodedetails.ERRORS = nodedetails.ERRORS + ", "+request.get_data().decode('utf-8')
    session.add(nodedetails)
    session.commit()
    return "OK"

@app.route("/commands", methods=["GET","POST"])
def handleGetCommands():
    session.commit()
    if request.method == "GET":
        nodeid = request.headers.get("X-NODE-ID")
        print(nodeid)
        nodedetails = session.query(NODES).filter(NODES.id == nodeid).first()
        session.rollback()
        return nodedetails.COMMAND_LIST
    if request.method == "POST":
        nodeid = request.headers.get("X-NODE-ID")
        print(nodeid)
        nodedetails = session.query(NODES).filter_by(id=nodeid).first()
        commandlist = nodedetails.COMMAND_LIST.split(",")
        commandlist.remove(request.get_data().decode('utf-8'))
        nodedetails.COMMAND_LIST = ",".join(commandlist)
        print(nodedetails.COMMAND_LIST)
        session.add(nodedetails)
        session.commit()
        return "OK"

@app.route("/stimulus")
def handleGetStimulus():
    nodeid = request.headers.get("X-NODE-ID")
    nodedetails = session.query(NODES).filter(NODES.id == nodeid).first()
    return nodedetails.STIMULUS

@app.route("/vpnlocation")
def handleGetLocation():
    nodeid = request.headers.get("X-NODE-ID")
    nodedetails = session.query(NODES).filter(NODES.id == nodeid).first()
    return nodedetails.VPN_LOCATION