#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import config
import math
import datetime
import numpy as np
from geopy.distance import vincenty
from models import Department, Location, Course, Section, Session

def score_free_days(matrix, preferred_num_free_days):
    num_free_days = 0

    for row in matrix:
        courses = np.nonzero(row)
        if len(courses) == 0:
            num_free_days += 1

    score = 1 - (abs(num_free_days - preferred_num_free_days) / float(4))
    if score < 0:
        score = 0

    return score

def average_time_delta(times, since, ignoreAfter):
    deltatimes = [datetime.timedelta(0, 0, 0, 0, time.minute, time.hour) for time in times]
    deltatimeSince = datetime.timedelta(0, 0, 0, 0, since.minute, since.hour)
    if len(deltatimes) == 0:
        return None

    deltas = [deltatime - deltatimeSince for deltatime in deltatimes]
    if ignoreAfter:
        correctDeltas = [datetime.timedelta(0) if delta.total_seconds() > 0 else -delta for delta in deltas]
    else:
        correctDeltas = [datetime.timedelta(0) if delta.total_seconds() < 0 else delta for delta in deltas]

    return (reduce(lambda x, y: x + y, correctDeltas) / len(correctDeltas))

def score_time_boundaries(schedule, preferred_start_time, preferred_end_time):
    start_times = []
    end_times = []

    for i in range(0, len(schedule)):
        col = schedule[i]
        stripped_col = col[np.nonzero(col)]

        if len(stripped_col) == 0:
            continue

        start_times.append(stripped_col[0].start_time)
        end_times.append(stripped_col[len(stripped_col) - 1].end_time)

    start_time_delta = average_time_delta(start_times, preferred_start_time, True)
    end_time_delta = average_time_delta(end_times, preferred_end_time, False)

    delta_sum = (start_time_delta + end_time_delta)

    score = 1 - (abs(delta_sum.total_seconds()) / float(18000))
    if score < 0:
        score = 0

    return score

def score_physical_distances(schedule):
    scores = []

    for i in range(0, len(schedule)):
        col = schedule[i]
        sessions = col[np.nonzero(col)]
        uniqueSessions = []

        for session in sessions:
            if not session in uniqueSessions:
                uniqueSessions.append(session)

        for j in range(0, len(uniqueSessions)):
            if j + 1 == len(uniqueSessions):
                break

            s1 = uniqueSessions[j]
            s2 = uniqueSessions[j + 1]

            c1 = s1.location.coordinatesTuple()
            c2 = s2.location.coordinatesTuple()

            # Vincenty distance between two coordinates
            cd = vincenty(c1, c2).meters

            t1 = s1.end_time
            t2 = s2.start_time

            td = datetime.timedelta(0, 0, 0, 0, t2.minute, t2.hour) - datetime.timedelta(0, 0, 0, 0, t1.minute, t1.hour)

            # 50 m/min is a reasonable walking speed
            reasonable_distance = 50 * (td.total_seconds() / 60)

            reasonability_score = cd - reasonable_distance
            scores.append(reasonability_score)

            # print("%d meters distance and %d minute time distance between %s and %s, reasonability score: %d" % (cd, td.total_seconds() / 60, s1.section.course.name, s2.section.course.name, reasonability_score))

    if len(scores) == 0:
        return 1

    max_deviation = max(scores)
    score = 1 - (max_deviation / float(1000))
    if score < 0:
        score = 0

    return score


def score(matrix, preferred_start_time, preferred_end_time, preferred_num_free_days):
    days_of_week_score = score_free_days(matrix, preferred_num_free_days)
    time_boundaries_score = score_time_boundaries(matrix, preferred_start_time, preferred_end_time)
    distance_score = score_physical_distances(matrix)

    final_score = days_of_week_score + time_boundaries_score + distance_score
    return final_score
