import config
from pyquery import PyQuery as pq

class Availability:
    def __init__(self, seats, occupied_seats, wl_seats, occupied_wl_seats):
        self.seats = seats
        self.occupied_seats = occupied_seats
        self.wl_seats = wl_seats
        self.occupied_wl_seats = occupied_wl_seats

    def available_seats(self):
        return self.seats - self.occupied_seats

    def available_wl_seats(self):
        return self.wl_seats - self.occupied_wl_seats

    def is_available(self):
        return (self.available_seats() != 0 or self.available_wl_seats() != 0)

    def __str__(self):
        return "<Availability> %s. %d/%d seats available, %d/%d waitlist seats available" % ("Available" if self.is_available() else "Not available", self.available_seats(), self.seats, self.available_wl_seats(), self.wl_seats)


def check_availability(crn):
    oscar_uri = "https://oscar.gatech.edu/pls/bprod/bwckschd.p_disp_detail_sched?term_in=%s&crn_in=%d" % (config.COURSE_TERM, crn)
    d = pq(url=oscar_uri)

    seats_row = d(".dddefault > .datadisplaytable tr").eq(1);
    wl_row = d(".dddefault > .datadisplaytable tr").eq(2);

    total_seats = int(seats_row.find("td").eq(0).text());
    occupied_seats = int(seats_row.find("td").eq(1).text());

    total_wl_seats = int(wl_row.find("td").eq(0).text());
    occupied_wl_seats = int(wl_row.find("td").eq(1).text());

    return Availability(total_seats, occupied_seats, total_wl_seats, occupied_wl_seats)
