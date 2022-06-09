from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, MetaData
import sqlalchemy, json
import re
import csv, time
engine = create_engine("mysql+pymysql://$$$$:$$$$@$$$$/SciEx?charset=utf8mb4", echo=True)
sessionm = sessionmaker(bind=engine)
base = declarative_base()

class VPN_LOCATIONS(base):
    __tablename__ = "VPN_LOCATIONS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    VPN_LOCATION = Column(String(150), nullable=False)
    INSTANCES = Column(Integer)

class STIMULI(base):
    __tablename__ = "STIMULI"

    id = Column(Integer, primary_key=True, autoincrement=True)
    STIMULUS = Column(String(150), nullable=False)
    INSTANCES = Column(Integer)

class NODES(base):
    __tablename__ = "NODES"

    id = Column(Integer, primary_key=True, autoincrement=True)
    VPN_LOCATION = Column(String(150))
    STIMULUS = Column(String(150))
    ERRORS = Column(Text)
    COMMAND_LIST = Column(String(400))

class RESULTS(base):
    __tablename__ = "RESULTS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    RESULT = Column(Text)
    STIMULUS = Column(String(150))
    LOCATION = Column(String(150))

class COUNTRESULT(base):
    __tablename__ = "LINERESULTS"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    RESULTID = Column(Integer)
    KEYCOUNT = Column(Integer)
    LINES = Column(Integer)
    STIMULUS = Column(String(150))
    LOCATION = Column(String(150))

base.metadata.create_all(engine)

keyterms = ["tested", "positive", "testing", "isolation", "covid", "covld", "clinic", "pcr"]
locationcount = {}
locationcountall = {}

session = sessionm()
results = session.query(RESULTS).all()

for item in results:
    itemcount = 0
    itemlines = 0
    itemlines += len(re.findall("(.+)", item.RESULT))
    try:
        locationcountall[item.LOCATION] = locationcountall[item.LOCATION] + len(re.findall("(.+)", item.RESULT))
    except KeyError:
        locationcountall[item.LOCATION] = 1
    for string in keyterms:
        if string in str(item.RESULT):
            itemcount += len(re.findall(string, item.RESULT))
            try:
                locationcount[item.LOCATION] = locationcount[item.LOCATION] + len(re.findall(string, item.RESULT))
            except KeyError:
                locationcount[item.LOCATION] = 1
    temp = COUNTRESULT(RESULTID = item.id, KEYCOUNT = itemcount, LINES = itemlines, STIMULUS = item.STIMULUS, LOCATION = item.LOCATION)
    session.add(temp)
    session.commit()

print(f"{len(results)} Autocomplete Searches processed.")

results = {}
country_mapper = {
    "AE-Dubai-dxb": ["","","United Arab Emirates"],
    "AL-Tirana-tia": ["","","Albania"],
    "AR-Buenos-Aires-eze": ["","", "Argentina"],
    "AU-Adelaide-adl": ["","South Australia", "Australia"],
    "AU-Brisbane-bne": ["","Queensland", "Australia"],
    "AU-Melbourne-mel": ["","Victoria", "Australia"],
    "AU-Perth-per": ["","Western Australia", "Australia"],
    "AU-Sydney-syd": ["","New South Wales", "Australia"],
    "BR-Sao-Paulo-gru": ["","Sao Paulo", "Brazil"],
    "CA-Montreal-yul": ["","Quebec", "Canada"],
    "CA-Toronto-tor": ["","Ontario", "Canada"],
    "CA-Vancouver-yvr": ["","British Columbia", "Canada"],
    "CH-Zurich-zrh": ["","","Switzerland"],
    "CL-Santiago-scl": ["","Metropolitana", "Chile"],
    "CR-San-Jose-sjo": ["","", "Costa Rica"],
    "FI-Helsinki-hel": ["","", "Finland"],
    "HR-Zagreb-zag": ["","", "Croatia"],
    "IN-Mumbai-bom": ["","Maharashtra", "India"],
    "IN-New-Delhi-del": ["","Delhi", "India"],
    "IS-Reykjavik-rkv": ["","", "Iceland"],
    "JP-Tokyo-nrt": ["","Tokyo", "Japan"],
    "KR-Seoul-sel": ["","", "Korea, South"],
    "MD-Chisinau-kiv": ["","", "Moldova"],
    "MX-Guadalajara-gdl": ["","Jalisco", "Mexico"],
    "MY-Kuala-Lumpur-kul": ["","W.P. Kuala Lumpur", "Malaysia"],
    "NZ-Auckland-akl": ["","", "New Zealand"],
    "PE-Lima-lim": ["","Lima", "Peru"],
    "RO-Bucharest-otp": ["","","Romania"],
    "RS-Belgrade-beg": ["","", "Serbia"],
    "SG-Singapore-sin": ["","","Singapore"],
    "SI-Ljubljana-lju": ["","", "Slovenia"],
    "US-Ashburn-iad": ["Loudoun", "Virginia", "US"],
    "US-Atlanta-atl": ["Fulton", "Georgia", "US"],
    "US-Boston-bos": ["Suffolk", "Massachusetts", "US"],
    "US-Charlotte-clt": ["Mecklenburg", "North Carolina", "US"],
    "US-Chicago-chi": ["Cook", "Illinois", "US"],
    "US-Cincinnati-cvg": ["Hamilton", "Ohio", "US"],
    "US-Dallas-dal": ["Dallas", "Texas", "US"],
    "US-Denver-den": ["Denver", "Colorado", "US"],
    "US-Houston-hou": ["Harris", "Texas", "US"],
    "US-Las-Vegas-las": ["Clark", "Nevada", "US"],
    "US-Los-Angeles-lax": ["Los Angeles", "California", "US"],
    "US-Miami-mia": ["Miami-Dade", "Florida", "US"],
    "US-New-Orleans-msy": ["Orleans", "Louisiana", "US"],
    "US-New-York-nyc": ["New York", "New York", "US"],
    "US-Phoenix-phx": ["Maricopa", "Arizona", "US"],
    "US-San-Jose-sjc": ["Santa Clara", "California", "US"],
    "US-Seattle-sea": ["King", "Washington", "US"],
}

covidFile = open("01-28-2022.csv", "r")
covidData = csv.reader(covidFile)
locList = []
outputFile = open("correlation.csv", "w", newline='')
outputCSV = csv.writer(outputFile, delimiter= ",", quoting=csv.QUOTE_MINIMAL)
outputCSV.writerow(["Location", "Count", "Samples", "Percentage", "InfectionRate"])

for row in covidData:
    locList.append(row)

for key in sorted(locationcount, reverse=True):
    value = locationcount[key]
    totalcount = locationcountall[key]
    percentage = value/totalcount
    admin2 = country_mapper[key][0]
    province_state = country_mapper[key][1]
    country = country_mapper[key][2]
    row_final = None
    #print(f"Country: {country}; Province/State: {province_state}; LGA/Locality: {admin2}")
    for row in locList:
        if row[3] == country:
            if  row[1] == admin2:
                if  row[2] == province_state:
                    row_final = row
    #print(f"{key}: {value} out of {totalcount}: {percentage}")
    outputCSV.writerow([key, value, totalcount, percentage, row_final[12]])

lineresult = session.query(COUNTRESULT).all()
outputFile.close()

rawFile = open("raw.csv", "w", newline='')
rawCSV = csv.writer(rawFile, delimiter= ",", quoting=csv.QUOTE_MINIMAL)
rawCSV.writerow(["ID", "Count", "Samples", "Stimulus", "Location"])

for item in lineresult:
    rawCSV.writerow([item.id, item.KEYCOUNT, item.LINES, item.STIMULUS, item.LOCATION])

time.sleep(5)
rawFile.close()