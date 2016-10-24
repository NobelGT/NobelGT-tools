#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy as np
import datetime

def sch2str(sch):
    results = []

    for day in sch:
        result = ''
        for session in day:
            if session is None:
                slotText = "|  % 10s" % ('')
            else:
                section = session.section
                course = section.course
                slotText = "|  % 10s" % (course.department_code + course.course_number)
            result += slotText

        results.append(result)

    return "\n\n" + "\n".join(results)

def sch2tab(tpl):
    startDt = datetime.timedelta(0, 0, 0, 0, 30, 6)
    addDt = datetime.timedelta(0, 0, 0, 0, 30)

    sch = tpl[2]

    result = '<div class="panel panel-default">'
    result += '<div class="panel-heading">Solution (Confidence: %.2f / 3)</div>' % (-1 * tpl[0])
    result += '<table class="table table-bordered">'
    result += '<tr><th>Time</th><th>Monday</th><th>Tuesday</th><th>Wednesday</th><th>Thursday</th><th>Friday</th></tr>'

    for i in range(0, len(sch[0])):
        startTime = startDt + i * addDt

        shours, sremainder = divmod(startTime.seconds, 3600)
        sminutes, sseconds = divmod(sremainder, 60)

        endTime = startDt + (i+1) * addDt

        ehours, eremainder = divmod(endTime.seconds, 3600)
        eminutes, eseconds = divmod(eremainder, 60)

        result += '<tr><td class="col-md-2">%02d:%02d - %02d:%02d</td>' % (shours, sminutes, ehours, eminutes)

        for j in range(0, len(sch) - 2):
            sess = sch[j][i]

            if sess is None:
                result += '<td class="col-md-2">'
                result += "<br><br>"
            else:
                result += '<td class="col-md-2 bg-info">'
                result += sess.section.course.department.code + " " + sess.section.course.course_number + "<br>"
                result += sess.section.code + " (" + str(sess.section.crn) + ")<br>"
                result += sess.location.name + " " + sess.room

            result += "</td>"

        result += '</tr>'

    result += "</table></div>"

    return result