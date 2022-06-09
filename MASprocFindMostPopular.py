from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
import sqlalchemy, json
import re
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

countdict = {}
totalcount = 0

session = sessionm()

results = session.query(RESULTS).all()
for item in results:
    a = re.findall("(.+)", item.RESULT)
    for match in a:
        if "test" in match:
            totalcount = totalcount + 1
            try:
                countdict[match] = countdict[match] + 1
            except KeyError:
                countdict[match] = 1

print(totalcount)

for item in sorted(countdict, key=countdict.get, reverse=True):
    text = str(countdict[item])
    item = item.strip("\r")
    print(item + ": " + text)
