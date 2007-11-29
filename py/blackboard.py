#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef 
Blackboard class
"""

import globalvars
from constants import *

import scraft
from scraft import engine as oE

#------------
# Черная доска 
# Любой объект может сделать запись
# или прочитать записи других объектов
#------------

class BlackBoard:
    def __init__(self):
        self.Records = {}
        
    def Update(self, tag, data = None):
        try:
            if not self.Records.has_key(tag):
                self.ClearTag(tag)
            
            #о сделанных заказах
            #записываем информацию об ингредиентах
            if tag in (BBTag_Ingredients, BBTag_Recipes):
                if not self.Records[tag].has_key(data["type"]):
                    self.Records[tag][data["type"]] = 0
                self.Records[tag][data["type"]] = max(0, self.Records[tag][data["type"]] + data["delta"])
                if self.Records[tag][data["type"]] == 0:
                    self.Records[tag].pop(data["type"])
                    
            #о курсоре и его содержимом
            elif tag == BBTag_Cursor:
                for tmp in data.keys():
                    self.Records[BBTag_Cursor][tmp] = data[tmp]
                
            #о событиях, связанных с подсказками
            #хранится очередь событий, которые удаляются
            #по одной штуке в порядке появления
            elif tag == BBTag_Hints:
                self.Records[tag].append(data)
        except:
            pass
        
        
    def ClearTag(self, tag):
        if tag == BBTag_Hints:
            self.Records[tag] = []
        else:
            self.Records[tag] = {}
        
    def Inspect(self, tag, parameter = None):
        try:
            if not self.Records.has_key(tag):
                self.ClearTag(tag)
                #self.Records[tag] = {}
            if tag in (BBTag_Ingredients, BBTag_Cursor, BBTag_Recipes):
                return self.Records[tag]
            elif tag == BBTag_Hints:
                if len(self.Records[tag]) > 0:
                    return self.Records[tag].pop(0)
                else:
                    return None
        except:
            return None
        
    
    
