#!/usr/bin/python
# -*- coding: utf-8 -*-

import parse_general
import parse_pictocast
import sms_sender
import weather_fetcher
import message_writer

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: smsblue.py url number days")
        exit()
    
    url = sys.argv[1]
    number = sys.argv[2]
    days = sys.argv[3]
    
    wf = weather_fetcher.WeatherFetcher()
    general, picto = wf.fetch(url)
   
    mw = message_writer.PolishMessageWriter()
    message = mw.write_general_message(general[:3])
    print message
   
   # ss = sms_sender.SMSSender("pawel.szostek@gmail.com", "30cca6d85c3a3e77169fcff6a9afcc58")
   # r = ss.send(number=number, message=message)