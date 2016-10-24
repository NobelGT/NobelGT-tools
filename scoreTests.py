import config
import math
import time, datetime
import numpy as np
import score
from models import Department, Location, Course, Section, Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

DBSession = sessionmaker(bind=engine)
session = DBSession()

crns = [83052, 80684, 89435, 87481, 89599, 90968]

schedule = np.empty(7, dtype=object)
for i in range(0,7):
    schedule[i] = np.empty(31, dtype=object)

for crn in crns:
    section = session.query(Section).filter(Section.crn == crn).first()

    if section is not None:
        sessions = section.sessions

        for sess in sessions:
            tss = sess.timeslots
            for ts in tss:
                sday = int(math.floor(ts / 31))
                sslot = ts % 31

                schedule[sday][sslot] = sess

def datetimestrptime(time_string,time_fmt):
     t = time.strptime(time_string,time_fmt)
     return datetime.time(hour=t.tm_hour,minute=t.tm_min,second=t.tm_sec)

startTime = datetimestrptime("9:00 AM","%I:%M %p")
endTime = datetimestrptime("5:00 PM","%I:%M %p")
numOfFreeDays = 0

print(score.score(schedule, startTime, endTime, numOfFreeDays))
