#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import datetime, math
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import config

Base = declarative_base()

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=True)
    name = Column(Text, nullable=False)
    coordinates = Column(Text, nullable=True)

    def __repr__(self):
        return '<Location %r>' % (self.name)

    def coordinatesTuple(self):
        coords = [float(c) for c in self.coordinates.split(",")]

        if len(coords) == 0:
            return None

        return (coords[0], coords[1])

class Department(Base):
    __tablename__ = 'departments'

    code = Column(String(6), primary_key=True)
    name = Column(Text, nullable=False)

    def __repr__(self):
        return '<Department of %r (%r)>' % (self.name, self.code)

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    department_code = Column(String(128), ForeignKey('departments.code'), nullable=False)
    course_number = Column(String(10), nullable=False)
    credit_hours = Column(Integer, nullable=False)

    department = relationship(Department, back_populates="courses")

    def __repr__(self):
        return '<Course %r %r>' % (self.department_code, self.course_number)

class Section(Base):
    __tablename__ = 'sections'

    crn = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)

    course = relationship(Course, back_populates="sections")

    def __repr__(self):
        return '<Section %r of %r>' % (self.code, self.course)

    @hybrid_property
    def time_hash(self):
        coursePart = self.course.department_code + " " + self.course.course_number
        sectionPartArray = []
        for sess in self.sessions:
            sectionPartArray.extend(sess.timeslots)
        sectionPartArray.sort()
        sessionPart = str(sectionPartArray)

        return coursePart + ';' + sessionPart

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False)
    type = Column(String(20), nullable=False)
    instructors = Column(Text, nullable=False)
    start_time  = Column(Time, nullable=False)
    end_time  = Column(Time, nullable=False)
    section_crn = Column(Integer, ForeignKey('sections.crn'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    room = Column(String(20), nullable=True)

    section = relationship(Section, back_populates="sessions")
    location = relationship(Location, back_populates="sessions")

    def __repr__(self):
        return '<Session %r of %r>' % (self.id, self.section)

    @hybrid_property
    def timeslots(self):
        # We start 6.30
        zeroTime = datetime.timedelta(0, 0, 0, 0, 30, 6)
        startTime = datetime.timedelta(0, 0, 0, 0, self.start_time.minute, self.start_time.hour)
        endTime = datetime.timedelta(0, 0, 0, 0, self.end_time.minute, self.end_time.hour)

        startTimeSlot = math.floor((startTime - zeroTime).total_seconds() / 1800) + (self.day * config.SLOTS_PER_DAY)
        endTimeSlot = math.floor((endTime - zeroTime).total_seconds() / 1800) + (self.day * config.SLOTS_PER_DAY)
        return range(int(startTimeSlot), int(endTimeSlot + 1))

Location.sessions = relationship(Session, back_populates="location", cascade="all, delete, delete-orphan")
Department.courses = relationship(Course, back_populates="department", cascade="all, delete, delete-orphan")
Course.sections = relationship(Section, back_populates="course", cascade="all, delete, delete-orphan")
Section.sessions = relationship(Session, back_populates="section", cascade="all, delete, delete-orphan")

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
Base.metadata.bind = engine
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

engine.dispose()