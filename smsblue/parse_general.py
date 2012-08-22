#!/usr/bin/python
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
import datetime

class DayGeneral(object):
    def __init__(self, name, date=None, place=None, t_high=None, t_low=None, wind=None, uv=None, sunshine=None, precip=None):
        self.name = name
        self.date = date
        self.place = place
        self.t_high = t_high
        self.t_low = t_low
        self.wind = wind
        self.uv = uv
        self.sunshine = sunshine
        self.precip = precip
    
    def __str__(self):
        return "%s: name=%s, date=%s, place=%s t_high=%d, t_low=%d, wind=%d, uv=%s,\
sunshine=%d, precip=%s" % (self.__class__, self.name, str(self.date), self.place,\
    self.t_high, self.t_low, self.wind, str(self.uv), self.sunshine, self.precip)


class IParser():
    htmlCodes = [
    ['&', '&amp;'],
    ['<', '&lt;'],
    ['>', '&gt;'],
    ['"', '&quot;'],
    ]
    htmlCodesReversed = htmlCodes[:]
    htmlCodesReversed.reverse()

    def unescape(self, html, codes=htmlCodesReversed):
        """ Returns the ASCII decoded version of the given HTML string. This does
            NOT remove normal HTML tags like <p>. It is the inverse of htmlEncode()."""
        for code in codes:
            html = html.replace(code[1], code[0])
        return html

    def __init__(self):
        self._parsed_ = None
        self._days = []

    def parse(self, content):
        if not self._days:
            self._parse(content)
        return self._days

    def _parse(self, content):
        pass

        
class GeneralParser(HTMLParser, IParser, object):
    def __init__(self):
        HTMLParser.__init__(self)
        IParser.__init__(self)
        self._place = None
        self._inside_picto = False
        self._inside_day = False
        self._inside_days = False
        self._inside_days_th = False
        self._inside_value_td = False
        self._inside_values = False 
        
        self._inside_temp_high = False
        self._after_temp_high = False
        self._inside_temp_low = False
        self._inside_wind = False
        self._inside_uv = False
        self._after_uv = False
        self._inside_sunshine = False
        self._inside_precip = False
        
        self._embedded_table = False
        
        self._cur_day_idx = 0 
        
    def handle_starttag(self, tag, attributes):
        if tag == "meta" and ("property", "og:locality") in attributes:
            for name, value in attributes:
                if name == "content":
                    self._place = value
        if tag == "table" and ("class", "picto") in attributes:
            self._inside_picto = True
            return
        if not self._inside_picto:
            return
        if self._inside_picto and tag == "table":
            self._embedded_table = True
        if tag == "tr" and ("class", "days") in attributes:
            self._inside_days = True
        if tag == "span" and ("class", "day") in attributes:
            self._inside_day = True
        if tag == "th" and self._inside_days:
            self._inside_days_th = True
        if tag == "tr" and ("class", "temp") in attributes:
            if not self._inside_temp_low and not self._inside_temp_high and not self._after_temp_high:
                self._inside_temp_high = True
            elif self._after_temp_high:
                self._inside_temp_low = True
        if tag == "tr" and ("class", "wind") in attributes:
            self._inside_wind = True
        if tag == "tr" and ("class", "uvindex") in attributes:
            if not self._inside_uv and not self._inside_sunshine and not self._after_uv:
                self._inside_uv = True
            elif self._after_uv:
                self._inside_sunshine = True
        if tag == "tr" and ("class", "precipitation") in attributes:
            self._inside_precip = True
            
    def get_cur_day(self):
        if self._cur_day_idx == -1:
            raise StopIteration
        return self._days[self._cur_day_idx]
    
    def reset_cur_day(self):
        self._cur_day_idx = 0 
    
    def incr_cur_day(self):
        self._cur_day_idx += 1
    
    def handle_data(self, content):
        content = content.strip()
        if not content:
            return
        if self._inside_day:
            self._days.append(DayGeneral(content))
        elif self._inside_days and not self._inside_days_th:
            day, month = content.split('.')
            day = day.strip()
            today = datetime.date.today()
            self._days[-1].date = datetime.date(today.year, int(month), int(day))
        elif self._inside_values:
            content = content.strip()
            content = self.unescape(content)
            if self._inside_temp_high:
                content = content[:-2]
                self.get_cur_day().t_high = int(content)
            elif self._inside_temp_low:
                content = content[:-2]
                self.get_cur_day().t_low = int(content)
            elif self._inside_wind:
                self.get_cur_day().wind = int(content)
            elif self._inside_uv:
                self.get_cur_day().uv = int(content)
            elif self._inside_sunshine:
                self.get_cur_day().sunshine = int(content)
            elif self._inside_precip:
                if content == "--":
                    content = 0
                self.get_cur_day().precip = str(content)
    
    def handle_endtag(self, tag):
        if not self._inside_picto:
            return
        elif tag == "table":
            if self._embedded_table:
                self._embedded_table = False
            elif self._inside_picto:
                self._inside_picto = False
        elif tag == "span" and self._inside_day:
            self._inside_day = False
        elif tag == "th" and self._inside_days_th:
            self._inside_days_th = False
        elif tag == "tr":
            if self._inside_days:
                self._inside_days = False
            elif self._inside_values:
                self._inside_values = False
            if self._inside_temp_high:
                self._inside_temp_high = False
                self._after_temp_high = True
                self.reset_cur_day()
            elif self._inside_temp_low:
                self._inside_temp_low = False
                self.reset_cur_day()
            elif self._inside_wind:
                self._inside_wind = False
                self.reset_cur_day()
            elif self._inside_uv:
                self._inside_uv = False
                self._after_uv = True
                self.reset_cur_day()
            elif self._inside_sunshine:
                self._inside_sunshine = False
                self.reset_cur_day()
            elif self._inside_precip:
                self._inside_precip = False
                self._after_temp_high = False
                self._inside_values = False
                self._after_uv = False
                self.reset_cur_day()
        elif tag == "th" and (self._inside_temp_high\
            or self._inside_temp_low\
            or self._inside_wind\
            or self._inside_uv\
            or self._inside_sunshine\
            or self._inside_precip):
                self._inside_values = True
        elif tag == "td" and self._inside_values:
            self.incr_cur_day()
    
    def _parse(self, content):
        self.reset()
        self.feed(content)
        for day in self._days:
            day.place = self._place
    
if __name__ == "__main__":
    g = GeneralParser()
    f = open("../kielce_pl_19836.html")
    f = "".join(f.readlines())
    l = g.parse(f)
    for d in l:
        print d