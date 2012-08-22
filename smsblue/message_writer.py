#!/usr/bin/python
# -*- coding: utf-8 -*-

from parse_general import DayGeneral
from parse_pictocast import DayDetailed

class MessageWriter(object):
    def __init__(self):
        pass
    
    def write_general_message(self, days):
        pass
    
    def write_detailed_message(self, days):
        pass

class PolishMessageWriter(MessageWriter):
    def __init__(self):
        MessageWriter.__init__(self)
        
    def _general_message(self, day):
        assert isinstance(day, DayGeneral)
        ret = ""
        ret += "%d.%d: " % (day.date.month, day.date.day)
        ret += "%d < %s < %d, " % (day.t_low, "temp", day.t_high)
        ret += "wiatr %d km/h, " % day.wind
        if day.uv:
            ret += "uv-index %d, " % day.uv
        ret += "%dh slonca, " % day.sunshine
        ret += "%smm opadu." % day.precip
        return ret

    def _detailed_message(self, day):
        assert isinstance(day, DayDetailed)

        ret = ""
        for w in day.hours:
            ret += "%s:00: %d*C %3.1fmm %d%% " % (w.hour, w.weather.temp, w.weather.precip, w.weather.precip_prob)
        return ret

    def write_general_message(self, days):
        assert isinstance(days, list)
        assert len(days) > 0

        place = days[0].place
        days = [self._general_message(d) for d in days]
        return "%s %s" % (place, " ".join(days))

    def write_detailed_message(self, days):
        assert isinstance(days, list)
        assert len(days) > 0

        place = days[0].place
        days = [self._detailed_message(d) for d in days]
        return "%s %s" % (place, " ".join(days))


class EnglishMessageWriter(MessageWriter):
    pass

if __name__ == "__main__":
    from parse_general import GeneralParser
    from parse_pictocast import PictocastParser
    g = GeneralParser()
    d = PictocastParser()
    with open("../kielce_pl_19836.html") as f:
        f = "".join(f.readlines())
        lg = g.parse(f)
    with open("../pictocast.html") as f:
        f = "".join(f.readlines())
        ld = d.parse(f)
    mw = PolishMessageWriter()
    msg = mw.write_detailed_message(ld[:1])
    msg += mw.write_general_message(lg[1:3])
    print(len(msg), msg)