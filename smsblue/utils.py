#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2

def get_place(url):
    parts = url.split('/')
    last_part = parts[-1]
    place_parts = last_part.split('_')
    place = place_parts[0]
    return place[0].upper() + place[1:]