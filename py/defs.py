#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Чтение данных о рецептах, конфигураций уровней
"""

import sys
import string, traceback
import scraft
from scraft import engine as oE
import globalvars
from configconst import *

#--------------------------
# Чтение данных о ресурсах
#--------------------------

def ReadResourceInfo():
    try:
        #define sprite classes
        for tmpTags in oE.ParseDEF(File_ResourceInfo).GetTag(u"MasterChef").Tags():
            for sprTag in tmpTags:
                oE.SstDefKlass(sprTag.GetContent(), sprTag)
        
        #define customer classes
        for sprTag in oE.ParseDEF(File_Animations).GetTag(u"MasterChef").GetTag(u"CustomerKlasses").Tags():
            oE.SstDefKlass(sprTag.GetContent(), sprTag)
        
        #read customer animations
        globalvars.CustomerAnimations = oE.ParseDEF(File_Animations).GetTag(u"MasterChef")#.Tags("Animation")
                
    except:
        oE.Log(u"Cannot read resources")
        sys.exit()
        

#--------------------------
# Чтение данных о рецептах
#--------------------------

def ReadCuisine():
    try:
        globalvars.CuisineInfo = oE.ParseDEF(File_Cuisine).GetTag(u"MasterChef")
        globalvars.RecipeInfo = oE.ParseDEF(File_Recipes).GetTag(u"MasterChef")
        
    except:
        oE.Log(u"Cannot read cuisine info")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()

#--------------------------
# Список уровней
#--------------------------

def ReadLevelProgress():
    try:
        globalvars.LevelProgress = oE.ParseDEF(File_LevelProgress).GetTag(u"MasterChef")
    except:
        oE.Log(u"Cannot read levels list")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()
        
#--------------------------
# Чтение глобальных настроек
#--------------------------

def ReadGameSettings():
    try:
        globalvars.GameSettings = oE.ParseDEF(File_GameSettings).GetTag("MasterChef").GetTag("GameSettings")
        globalvars.CustomersInfo = oE.ParseDEF(File_GameSettings).GetTag("MasterChef").GetTag("Customers")
        globalvars.ThemesInfo = oE.ParseDEF(File_GameSettings).GetTag("MasterChef").GetTag("Themes")
        globalvars.PowerUpsInfo = oE.ParseDEF(File_GameSettings).GetTag("MasterChef").GetTag("PowerUps")
        
    except:
        oE.Log(u"Cannot read global game settings")
        #sys.exit()
        
#------------------------
# Чтение настроек уровня
#------------------------

def ReadLevelSettings(filename):
    try:
        globalvars.LevelSettings = oE.ParseDEF(unicode(filename)).GetTag(u"Level")
        globalvars.Layout = {}
        ReadGameSettings()
        
        #override global game settings
        if globalvars.LevelSettings.GetCountTag(u"GameSettings") == 1:
            tmp = globalvars.LevelSettings.GetTag(u"GameSettings")
            for tmpIntAttr in ("newCustomerTimeMin", "newCustomerTimeMax",
                               "tokensGroupMin", "tokensGroupMax",
                               "minCorrectionAmount",
                               "ratesSum",
                               "basicRatesRatio", "neededRatesRatio", "neededToBasicRatio",
                               "neighbourBonus", "desiredNeighbourBonus",
                               "maxGroup", "minRateMultiplier",
                               "levelRatesMultiplier", "boardNeededMultiplier",
                               "maxColapsoidErrors"):
                if tmp.HasAttr(tmpIntAttr):
                    globalvars.GameSettings.SetIntAttr(tmpIntAttr, tmp.GetIntAttr(tmpIntAttr))
            for tmpFltAttr in ("tokensFallingTime", "shuffleTime", "magicWandConvertingTime",
                               "scrollBackTime", "burnCollapsoidTime"):
                if tmp.HasAttr(tmpFltAttr):
                    globalvars.GameSettings.SetFltAttr(tmpFltAttr, tmp.GetFltAttr(tmpFltAttr))
            for tmpBoolAttr in ("autoReleaseCustomer", "allowExtraIngredients", "exactRecipes"):
                if tmp.HasAttr(tmpBoolAttr):
                    globalvars.GameSettings.SetBoolAttr(tmpBoolAttr, tmp.GetBoolAttr(tmpBoolAttr))
                
        #override customer settings
        if globalvars.LevelSettings.GetCountTag(u"Customers") == 1:
            for tmp in globalvars.LevelSettings.GetTag(u"Customers").Tags():
                tmpCustomer = globalvars.CustomersInfo.GetSubtag(tmp.GetContent())
                for tmpIntAttr in ("heartsOnStart", "orderingTimeMin", "orderingTimeMax",
                                   "gotGiftTimeMin", "gotGiftTimeMax", "patientTimeMin", "patientTimeMax",
                                   "thankYouTime", "goAwayTime"):
                    if tmp.HasAttr(tmpIntAttr):
                        tmpCustomer.SetIntAttr(tmpIntAttr, tmp.GetIntAttr(tmpIntAttr))
                for tmpStrAttr in ("likes", "dislikes", "tips"):
                    if tmp.HasAttr(tmpStrAttr):
                        tmpCustomer.SetStrAttr(tmpStrAttr, tmp.GetStrAttr(tmpStrAttr))
                for tmpBoolAttr in ("takesIncompleteOrder", "allowsExcessIngredients"):
                    if tmp.HasAttr(tmpBoolAttr):
                        tmpCustomer.SetBoolAttr(tmpBoolAttr, tmp.GetBoolAttr(tmpBoolAttr))
        
    except:
        oE.Log(u"Cannot read level info from: "+filename)
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()
        

#------------------------
# Чтение размеров групп - для балансировки
#------------------------

def ReadGroups(filename):
    try:
        tmpDataIterator = oE.ParseDEF(unicode(filename)).GetTag(u"MasterChef").IterateTag(u"group")
        tmpGroups = {}
        while tmpDataIterator.Next():
            tmp = tmpDataIterator.Get()
            tmpGroups[tmp.GetFltAttr(u"rate")] = 0.25*tmp.GetFltAttr(u"max")+0.65*tmp.GetFltAttr(u"size")+0.1*tmp.GetFltAttr(u"min")
        return tmpGroups
    except:
        return {}
    
#-----------------------------------
# Возвращает подноду данной ноды с заданным значением заданного атрибута
#-----------------------------------

def GetTagWithAttribute(node, tag, attr, value):
    try:
        tmpIterator = node.IterateTag(tag)
        while tmpIterator.Next():
            if tmpIterator.Get().HasAttr(unicode(attr)):
                if tmpIterator.Get().GetStrAttr(unicode(attr)) == value:
                    return tmpIterator.Get()
        return None
    except:
        return None
        
    
    
    

