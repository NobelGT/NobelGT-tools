#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import json
import config
import datetime, time
from models import Department, Location, Course, Section, Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

DBSession = sessionmaker(bind=engine)
session = DBSession()

jsonfile = os.path.join(config.BASE_DIR, 'rip-oscar.json')
json_data=open(jsonfile).read()

data = json.loads(json_data)

dayDict = {'M':0, 'T':1, 'W':2, 'R':3, 'F':4, 'S':5, 'U': 6}

def clear_nonloc_data():
    courses = session.query(Course).all()
    depts = session.query(Department).all()
    sections = session.query(Section).all()
    sessions = session.query(Session).all()

    for db_objs in [courses, depts, sections, sessions]:
        for obj in db_objs:
            session.delete(obj)
            session.commit()

def datetimestrptime(time_string,time_fmt):
     t = time.strptime(time_string,time_fmt)
     return datetime.time(hour=t.tm_hour,minute=t.tm_min,second=t.tm_sec)

clear_nonloc_data()
for courseNode in data:
    code = courseNode['code']
    codeParts = code.split(" ")

    deptcode = codeParts[0].strip()
    courseno = codeParts[1].strip()

    dept = session.query(Department).filter(Department.code == deptcode).first()
    if dept is None:
        dept = Department(name=deptcode, code=deptcode)
        session.add(dept)
        session.commit()

    course = Course(name=courseNode['title'], department_code=dept.code, course_number=courseno, credit_hours=courseNode['creditHours'])
    session.add(course)
    session.commit()

    sectionNodes = courseNode['sections']
    for sectionNode in sectionNodes:
        crn = sectionNode['crn']
        code = sectionNode['section']

        section = Section(crn=crn, code=code, course_id=course.id)
        session.add(section)
        session.commit()

        sessNodes = sectionNode['sessions']
        for sessNode in sessNodes:
            times = sessNode['times'].split(" - ")

            startTime = datetimestrptime(times[0].upper(),"%I:%M %p")
            endTime = datetimestrptime(times[1].upper(),"%I:%M %p")

            days = sessNode['days']

            location = None
            if sessNode['location'] != 'TBA':
                lxn = sessNode['location'].rsplit(' ', 1)
                bldg = lxn[0]
                room = lxn[1]

                location = session.query(Location).filter(Location.name == bldg).first()
                if location is None:
                    location = Location(name=bldg)
                    session.add(location)
                    session.commit()

            type = sessNode['type'].replace('*', '')
            instructors = sessNode['instructors']

            for day in days:
                dayInt = dayDict[day]
                if location is None:
                    sess = Session(day=dayInt, type=type, instructors=instructors, start_time=startTime, end_time=endTime, section_crn=section.crn)
                else:
                    sess = Session(day=dayInt, type=type, instructors=instructors, start_time=startTime, end_time=endTime, section_crn=section.crn, location_id=location.id, room=room)
                session.add(sess)
                session.commit()

    if course.id % 10 == 0:
        print(str(course.id) + ': Added course ' + course.name)

print('Done')
