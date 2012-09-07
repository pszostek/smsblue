#!/usr/bin/python
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
from parse_general import IParser
from collections import namedtuple
import datetime

HourEntry = namedtuple("HourEntry", ["hour", "weather"], verbose=False)

class DaytimeWeather(object):
    def __init__(self, temp=None, temp_like=None, wind=None, wind_gusts=None, humid=None, precip=None, precip_prob=None):
        self.temp = temp
        self.temp_like = temp_like
        self.wind = wind
        self.wind_gusts = wind_gusts
        self.humid = humid
        self.precip = precip
        self.precip_prob = precip_prob
    
    def __str__(self):
        return "%s: temp=%s, temp_like=%s, wind=%s, wind_gusts=%s, humid=%s,\
precip=%s, precip_prob=%s" % (self.__class__, self.temp, self.temp_like,\
        self.wind, self.wind_gusts, self.humid, self.precip, self.precip_prob)  

class DayDetailed(object):
    def __init__(self, date=None, name=None, hours=None, place=None):
        """date = daytime.date('2012', '08', '05')
        name = 'Wednesday'
        place = 'Warsaw'
        dw = DaytimeWeather(temp=13, temp_like=15, wind=5, wind_gusts=6,
        humid = 70, precip="21", precip_prob=50)
        hours = [HourEntry(hour=1, dw), HourEntry(hour=3, dw), HourEntry(7,dw) ...]"""
        self.date = date
        self.name = name
        if hours is None:
            self.hours = {}
        else:
            self.hours = hours
        self.place = place

    def set_weather_for_hour(self, hour, weather):
        self.hours[hour] = weather

    def __str__(self):
        return "%s: %s, %s: %s" %\
        (self.__class__, self.date, self.name, ", ".join(str(h) for h in self.hours)) 


class PictocastParser(HTMLParser, IParser, object):
    TIME, TEMP, TEMP_LIKE, WIND, WIND_GUSTS, HUMID, PRECIP, PRECIP_PROB = range(0, 8)
    def __init__(self):
        HTMLParser.__init__(self)
        IParser.__init__(self)
        self._days = []
        self._embedded_tables = 0
        self._inside_time = False
        self._state = None
        self._even_pictodetail = False
        self._inside_values = False
        self._place = None
    
    def _reset_cur_hour(self):
        self._cur_hour = iter(self._days[-1].hours.keys()) 
    
    def handle_starttag(self, tag, attributes):

        if tag == "meta" and ("property", "og:locality") in attributes:
            for name, value in attributes:
                if name == "content":
                    self._place = value
        if tag == "table" and ("class", "pictodetail") in attributes:
            if self._embedded_tables is 0:
                if not self._even_pictodetail:
                    self._days.append(DayDetailed(place=self._place))
                self._even_pictodetail = not self._even_pictodetail
            self._embedded_tables += 1
        elif tag == "tr":
            if ("class", "time") in attributes:
                self._state = self.TIME
                self._reset_cur_hour()
            elif ("class", "temp") in attributes:
                self._state = self.TEMP
                self._reset_cur_hour()
            elif self._state is self.TEMP:
                self._state = self.TEMP_LIKE
                self._reset_cur_hour()
            elif self._state is self.TEMP_LIKE:
                self._state = self.WIND
                self._reset_cur_hour()
            elif self._state is self.WIND:
                self._state = self.WIND_GUSTS
                self._reset_cur_hour()
            elif self._state is self.WIND_GUSTS:
                self._state = self.HUMID
                self._reset_cur_hour()
            elif self._state is self.PRECIP and ("class", "precipitation") in attributes:
                self._state = self.PRECIP_PROB
                self._reset_cur_hour()
            elif ("class", "precipitation") in attributes:
                self._state = self.PRECIP
                self._reset_cur_hour()

        elif tag == "th" and self._state is not None:
            self._inside_values = False
    
    def handle_endtag(self, tag):
        if tag == "table" and self._embedded_tables:
            self._embedded_tables -= 1
        elif tag == "tr" and self._state is self.PRECIP_PROB:
            self._state = None
        elif tag == "th" and self._state is not None:
            self._inside_values = True
        if not self._embedded_tables:
            self._inside_values = False

    def handle_data(self, s):
        s = s.strip()
        if self._even_pictodetail:
            name, date = s.split(' ')
            date = [int(x) for x in date.split('.')]
            date = datetime.date(date[2], date[1], date[0])
            self._days[-1].name = name
            self._days[-1].date = date
        if not s:
            return
        if self._embedded_tables and not self._even_pictodetail:
            pass
        if self._inside_values:
            if   self._state is self.TIME:
                hour = int(s[:2])
                self._days[-1].set_weather_for_hour(hour, DaytimeWeather())
            elif self._state is self.TEMP:
                self._days[-1].hours[self._cur_hour.next()].temp = int(s.split(' ')[0])
            elif self._state is self.TEMP_LIKE:
                self._days[-1].hours[self._cur_hour.next()].temp_like = s[:-2]
            elif self._state is self.WIND:
                self._days[-1].hours[self._cur_hour.next()].wind = int(s)
            elif self._state is self.WIND_GUSTS:
                self._days[-1].hours[self._cur_hour.next()].wind_gusts = int(s)
            elif self._state is self.HUMID:
                self._days[-1].hours[self._cur_hour.next()].humid = int(s[:-2])
            elif self._state is self.PRECIP:
                if s == "-":
                    s = 0.0
                else:
                    s = float(s)
                self._days[-1].hours[self._cur_hour.next()].precip = s
            elif self._state is self.PRECIP_PROB:
                self._days[-1].hours[self._cur_hour.next()].precip_prob = int(s[:-2])
    
    def _parse(self, content):
        self.reset()
        self.feed(content)

if __name__ == "__main__":
    f = open("../pictocast.html")
    f = "".join(f.readlines())
    g = PictocastParser()
    l = g.parse(f)
    for d in l:
        for h in d.hours:
            print d.date, d.name, h, str(d.hours[h])