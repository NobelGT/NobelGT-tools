#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import config
import math
import numpy as np
import datetime
from models import Department, Location, Course, Section, Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Queue import PriorityQueue
from score import score
import heapq
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

DBSession = sessionmaker(bind=engine)
session = DBSession()

slotsPerDay = 31

funscore = 0

def solve(box, matrix, coursesGotten, slns):
    #print 'Called for %d' % box
    # Boxes are down-to-bottom first
    day = int(math.floor(box / config.SLOTS_PER_DAY))
    slot = box % config.SLOTS_PER_DAY

    # Check if we placed all courses
    allDone = True
    for course, inserted in coursesGotten.iteritems():
        if not inserted:
            allDone = False
            break

    # If so, return result
    if allDone:
        global funscore
        priority = funscore + -1 * score(matrix)
        funscore += 1

        newMatrix = np.empty(len(matrix), dtype=object)
        for i in range(0, len(matrix)):
            newMatrix[i] = np.empty(len(matrix[i]), dtype=object)
            for j in range(0, len(matrix[i])):
                newMatrix[i][j] = matrix[i][j]

        heapq.heappush(slns, (priority, newMatrix))

        print 'Found solution' + str(len(slns)) + '.'

        return

    # If we're outside the matrix and dont have a solution
    if day >= len(matrix):
        return

    if matrix[day][slot] is None:
        for course, alreadyInserted in coursesGotten.iteritems():
            if not alreadyInserted:
                sections = course.sections

                timehashesAddedHere = {}

                for section in sections:
                    timehash = section.time_hash

                    if timehash in timehashesAddedHere:
                        continue

                    sessions = section.sessions
                    sectionTimeslots = []
                    useThisSection = False

                    for sess in sessions:
                        ts = sess.timeslots
                        sectionTimeslots.extend(ts)

                    sectionTimeslots.sort()
                    #print sectionTimeslots
                    #print box
                    if len(sectionTimeslots) > 0 and sectionTimeslots[len(sectionTimeslots) - 1] == box :
                        useThisSection = True

                    if useThisSection:
                        timehashesAddedHere[timehash] = True
                        #print 'Trying and adding ' + timehash

                        # Apply all of the sessions to our map
                        for sess in sessions:
                            tss = sess.timeslots
                            for ts in tss:
                                sday = int(math.floor(ts / config.SLOTS_PER_DAY))
                                sslot = ts % config.SLOTS_PER_DAY

                                matrix[sday][sslot] = sess

                        coursesGotten[course] = True

                        # Now keep solving
                        solve(box + 1, matrix, coursesGotten, slns)

                        # And now undo that change.
                        for sess in sessions:
                            tss = sess.timeslots
                            for ts in tss:
                                sday = int(math.floor(ts / config.SLOTS_PER_DAY))
                                sslot = ts % config.SLOTS_PER_DAY

                                matrix[sday][sslot] = None

                        coursesGotten[course] = False

        # Try leaving this box empty too
        solve(box + 1, matrix, coursesGotten, slns)

def getSolutions(courseCodes):
    solutions = []
    coursesGotten = {}
    for courseCode in courseCodes:
        course = session.query(Course).filter(Course.id == courseCode).first()
        if course is not None:
            coursesGotten[course] = False

    schedule = np.empty(7, dtype=object)
    for i in range(0, len(schedule)):
        schedule[i] = np.empty(config.SLOTS_PER_DAY, dtype=object)

    solve(0, schedule, coursesGotten, solutions)

    #print solutions[0]

    return solutions

#slns = getSolutions([1012, 844, 458, 463, 52, 732])
#slns = getSolutions([463, 844, 52, 458, 1012])
slns = getSolutions([458])

crns = [84194, 89596, 83052, 88625, 89372]
#crns = [84194, 89596, 83052, 80684, 88625, 89372]
#crns = [89596]

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

print(schedule in slns)