#!/usr/bin/python
# -*- coding: utf-8 -*-

from parse_general import DayGeneral
from parse_pictocast import DayDetailed

class IMessageWriter(object):
    def __init__(self):
        pass
    
    def write_message(self, days, *args):
        pass
    
    def predict_message_length(self, days, *args):
        pass

        
class GeneralMessageWriter(IMessageWriter):
    sample_day = None
    def __init__(self):
        import datetime
        IMessageWriter.__init__(self)
        if not self.__class__.sample_day:
            self.__class__.sample_day =\
            DayGeneral(name="wed", date=datetime.date(2012,8,2),\
            place="Warsaw", t_high=18, t_low=5, wind=12, uv=4,\
            sunshine=3, precip="<1")
        
        
class DetailedMessageWriter(IMessageWriter):
    sample_day = None
    
    def __init__(self):
        import datetime
        from parse_pictocast import HourEntry, DaytimeWeather
        IMessageWriter.__init__(self)
        _dw = DaytimeWeather(temp=13, temp_like=15, wind=5, wind_gusts=6, humid = 70, precip=5.0, precip_prob=50)
        if not self.__class__.sample_day:
            self.__class__.sample_day = \
                DayDetailed(datetime.date(2012, 8, 4), 'Wednesday',\
                place = 'Warsaw',\
                hours = [HourEntry(2, _dw), HourEntry(5, _dw), HourEntry(8, _dw),\
                HourEntry(11, _dw), HourEntry(14, _dw), HourEntry(17, _dw),\
                HourEntry(20, _dw), HourEntry(23, _dw)])
        
        
class PolishGeneralMessageWriter(GeneralMessageWriter):
    def __init__(self):
        GeneralMessageWriter.__init__(self)

    def _day_message(self, day, features):
        assert isinstance(day, DayGeneral)
        ret = []
        if 'TEMP' in features:
            ret.append("%d*C < %s < %d*C" % (day.t_low, "t", day.t_high))
        if 'WIND' in features:
            ret.append("%d km/h" % day.wind)
        if 'UV' in features:
            if day.uv:
                ret.append("uv-index %d" % day.uv)
        if 'SUNSHINE' in features:
            ret.append("%dh" % day.sunshine)
        if 'PRECIP' in features:
            ret.append("%smm" % day.precip)

        ret = ", ".join(ret)
        if 'DATE' in features:
            date = "%2.2d.%2.2d: " % (day.date.day, day.date.month)
            ret = date + ret
        return ret

    def write_message(self, days, features):
        assert isinstance(days, list)
        assert len(days) > 0

        days = [self._day_message(d, features) for d in days]
        return " ".join(days)
    
    def predict_message_length(self, days, features):
        return len(self.write_message([self.__class__.sample_day]*number_of_days, features))


class PolishDetailedMessageWriter(DetailedMessageWriter):
    def __init__(self):
        DetailedMessageWriter.__init__(self)

    def predict_message_length(self, number_of_days, features, hours):
        return len(self.write_message([self.__class__.sample_day]*number_of_days, features, hours))

    def _day_message(self, day, features, hours):
        assert isinstance(day, DayDetailed)
        if not len(features):
            raise RuntimeError("No features for detailed days specified")

        ret = []
        hours = set(hours).intersection([hour for hour in day.hours])
        hours = sorted(hours)
        for hour in hours:
            ret.append([])
            ret[-1].append("%sh:" % hour)
            if "TEMP" in features:
                ret[-1].append("%d*C" % day.hours[hour].temp)
            if "TEMP_LIKE" in features:
                ret[-1].append("fl %d*C" % day.hours[hour].temp_like)
            if "WIND" in features:
                ret[-1].append("%dkm/h" % day.hours[hour].wind)
            if "WIND_GUSTS" in features:
                ret[-1].append("g%dkm/h" % day.hours[hour].wind_gusts)
            if "HUMID" in features:
                ret[-1].append("h%d%%" % day.hours[hour].humid)
            if "PRECIP" in features:
                ret[-1].append("%3.1fmm" % day.hours[hour].precip)
            if "PRECIP_PROB" in features:
                ret[-1].append("%d%%" % day.hours[hour].precip_prob)

        hour_str = [" ".join(item) for item in ret]
        return ". ".join(hour_str)

    def write_message(self, days, features, hours):
        assert isinstance(days, list)
        assert len(days) > 0

        days = [self._day_message(d, features, hours) for d in days]
        return ' '.join(days)

        
class PolishMessageWriter(object):
    def __init__(self):
        self.detailed_writer = PolishDetailedMessageWriter()
        self.general_writer = PolishGeneralMessageWriter()

    def write_message(self, detailed_days, general_days, number_detailed, number_general, detailed_args, general_args, hours):
        message = detailed_days[0].place + " "
        message += self.detailed_writer.write_message(detailed_days[0:number_detailed], detailed_args, hours)
        message += '. '
        message += self.general_writer.write_message(general_days[number_detailed:number_detailed+number_general], general_args)
        return message
        
    def predict_message_length(self, detailed_days, general_days, \
        number_detailed, number_general, detailed_features,\
        general_features, hours):
        return len(self.write_message(detailed_days, general_days,\
            number_detailed, number_general, detailed_features,\
            general_features, hours))
        
        
class EnglishMessageWriter(IMessageWriter):
    pass


if __name__ == "__main__":
    from parse_general import GeneralParser
    from parse_pictocast import PictocastParser
    general_parser = GeneralParser()
    detailed_parser = PictocastParser()

    with open("../kielce_pl_19836.html") as html_file:
        html_file = "".join(html_file.readlines())
        days_general = general_parser.parse(html_file)
    with open("../pictocast.html") as html_file:
        html_file = "".join(html_file.readlines())
        days_detailed = detailed_parser.parse(html_file)

    writer = PolishMessageWriter()
    message = writer.write_message(days_detailed, days_general, 1, 1, ["TEMP", "PRECIP", "PRECIP_PROB"], ["TEMP", "DATE", "PRECIP"], [8,14,20] )
    print writer.predict_message_length(days_detailed, days_general, 1, 1, ["TEMP", "PRECIP", "PRECIP_PROB"], ["TEMP", "DATE"], [8,14,20])
    print len(message)
    print(message)
