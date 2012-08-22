#!/usr/bin/python
# -*- coding: utf-8 -*-

import parse_general
import parse_pictocast
import urllib2

class WeatherFetcher(object):
    def __init__(self):
        pass
    
    def fetch(self, url):
        general_url, pictocast_url = self._normalize_url(url)
        general_parser = parse_general.GeneralParser()
        pictocast_parser = parse_pictocast.PictocastParser()
        
        f = urllib2.urlopen(general_url)
        f = f.read()
        general_days = general_parser.parse(f)
        
        f =  urllib2.urlopen(pictocast_url)
        f = f.read()
        pictocast_days = pictocast_parser.parse(f)
        
        return general_days, pictocast_days
        
    def _normalize_url(self, url):
        parts = url.split('/')
        forecast_idx = parts.index("forecast")
        place_code = parts[forecast_idx+2]
        
        general_pattern = "http://www.meteoblue.com/en_US/weather/forecast/week/%s"
        pictocast_pattern = "http://www.meteoblue.com/en_US/weather/forecast/tab/%s/b/pictocast"
        return (general_pattern % place_code, pictocast_pattern % place_code) 
        
if __name__ == "__main__":
    import sys
    w = WeatherFetcher()
    g, p = w.fetch(sys.argv[1])
    #days = zip(g,p)
    #for day_g, day_p in days:
        #print str(day_g)
        #print str(day_p)
        #print ""
    from message_writer import PolishMessageWriter
    mw = PolishMessageWriter()
    print(mw.write_general_message(g[0]))
    print(mw.write_general_message(g[1]))
    print(mw.write_general_message(g[2]))
    print(mw.write_general_message(g[3]))
    print(mw.write_general_message(g[4]))
    print(mw.write_general_message(g[5]))