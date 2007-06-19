#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef 
Blackboard class
"""

import globalvars
from constants import *

#------------
# Черная доска 
# Любой объект может сделать запись
# или прочитать записи других объектов
#------------

class BlackBoard:
    def __init__(self):
        self.Records = {}
        
    def Update(self, tag, data = None):
        if not self.Records.has_key(tag):
            self.Records[tag] = {}
        #записываем информацию об ингредиентах
        if tag == BBTag_Ingredients:
            if not self.Records[tag].has_key(data["type"]):
                self.Records[tag][data["type"]] = 0
            self.Records[tag][data["type"]] = max(0, self.Records[tag][data["type"]] + data["delta"])
            if self.Records[tag][data["type"]] == 0:
                self.Records[tag].pop(data["type"])
        #о курсоре и его содержимом
        elif tag == BBTag_Cursor:
            for tmp in data.keys():
                self.Records[BBTag_Cursor][tmp] = data[tmp]
        
    def ClearTag(self, tag):
        self.Records[tag] = {}
        
    def Inspect(self, tag, parameter = None):
        if not self.Records.has_key(tag):
            self.Records[tag] = {}
        if tag in (BBTag_Ingredients, BBTag_Cursor):
            return self.Records[tag]
        
    
    
