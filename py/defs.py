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
from configconst import File_Cuisine, File_GameSettings, File_ResourceInfo, File_Animations, File_LevelProgress

#--------------------------
# Чтение данных о ресурсах
#--------------------------

def ReadResourceInfo():
    try:
        tmpResourceInfo = oE.ParseDEF(File_ResourceInfo).GetTag(u"MasterChef")
        tmpKlassesIterator = tmpResourceInfo.GetTag(u"IngredientKlasses").IterateTag(u"sprite")
        while tmpKlassesIterator.Next():
            tmp = tmpKlassesIterator.Get()
            oE.SstDefKlass(unicode(tmp.GetContent()), tmp)
        tmpKlassesIterator = tmpResourceInfo.GetTag(u"RecipeKlasses").IterateTag(u"sprite")
        while tmpKlassesIterator.Next():
            tmp = tmpKlassesIterator.Get()
            oE.SstDefKlass(unicode(tmp.GetContent()), tmp)
        tmpKlassesIterator = tmpResourceInfo.GetTag(u"PowerUpKlasses").IterateTag(u"sprite")
        while tmpKlassesIterator.Next():
            tmp = tmpKlassesIterator.Get()
            oE.SstDefKlass(unicode(tmp.GetContent()), tmp)
        tmpKlassesIterator = tmpResourceInfo.GetTag(u"PowerUpKlasses").IterateTag(u"font")
        while tmpKlassesIterator.Next():
            tmp = tmpKlassesIterator.Get()
            oE.SstDefKlass(unicode(tmp.GetContent()), tmp)
        tmpKlassesIterator = tmpResourceInfo.GetTag(u"ThemeKlasses").IterateTag(u"sprite")
        while tmpKlassesIterator.Next():
            tmp = tmpKlassesIterator.Get()
            oE.SstDefKlass(unicode(tmp.GetContent()), tmp)
        tmpKlassesIterator = tmpResourceInfo.GetTag(u"Comics").IterateTag(u"sprite")
        while tmpKlassesIterator.Next():
            tmp = tmpKlassesIterator.Get()
            oE.SstDefKlass(unicode(tmp.GetContent()), tmp)
        
        #read customer classes
        tmpResourceInfo = oE.ParseDEF(File_Animations).GetTag(u"MasterChef")
        tmpKlassesIterator = tmpResourceInfo.GetTag(u"CustomerKlasses").IterateTag(u"sprite")
        while tmpKlassesIterator.Next():
            tmp = tmpKlassesIterator.Get()
            oE.SstDefKlass(unicode(tmp.GetContent()), tmp)
        
        #read customer animations
        globalvars.CustomerAnimations = {}
        tmpAnimationsIterator = tmpResourceInfo.IterateTag(u"Animation")
        while tmpAnimationsIterator.Next():
            tmp = tmpAnimationsIterator.Get()
            tmpName = tmp.GetContent()
            globalvars.CustomerAnimations[tmpName] = {}
            tmpSequenceIterator = tmp.IterateTag(u"Sequence")
            while tmpSequenceIterator.Next():
                tmpSQ = tmpSequenceIterator.Get()
                globalvars.CustomerAnimations[tmpName][tmpSQ.GetStrAttr(u"name")] = \
                    { "frames": eval(tmpSQ.GetStrAttr(u"frames")),
                        #"fps": tmpSQ.GetIntAttr(u"fps"),
                        "loops": tmpSQ.GetIntAttr(u"loops") }
                
    except:
        oE.Log(u"Cannot read resources")
        sys.exit()
        

#--------------------------
# Чтение данных о рецептах
#--------------------------

def ReadCuisine():
    try:
        globalvars.CuisineInfo = { "Ingredients": {}, "Recipes": {} }
        tmpCuisineData = oE.ParseDEF(File_Cuisine).GetTag(u"MasterChef")
        tmpIngredientsIterator = tmpCuisineData.GetTag(u"Ingredients").IterateTag(u"Ingredient")
        while tmpIngredientsIterator.Next():
            tmp = tmpIngredientsIterator.Get()
            globalvars.CuisineInfo["Ingredients"][tmp.GetStrAttr(u"name")] = {
                "type": tmp.GetStrAttr(u"type"),
                "src": tmp.GetStrAttr(u"src"), "iconSrc": tmp.GetStrAttr(u"iconSrc") }
            
        tmpRecipesIterator = tmpCuisineData.GetTag(u"Recipes").IterateTag(u"Recipe")
        while tmpRecipesIterator.Next():
            tmp = tmpRecipesIterator.Get()
            globalvars.CuisineInfo["Recipes"][tmp.GetStrAttr(u"name")] = {
                "setting": tmp.GetStrAttr(u"setting"),
                "type": tmp.GetStrAttr(u"type"),
                "src": tmp.GetStrAttr(u"src"),
                "emptySrc": tmp.GetStrAttr(u"emptySrc"),
                "price": tmp.GetIntAttr(u"price"),
                "readyAt": tmp.GetIntAttr(u"readyAt"),
                "requires": eval(tmp.GetStrAttr(u"requires"))
            }
        
    except:
        oE.Log(u"Cannot read cuisine info")
        sys.exit()

#--------------------------
# Список уровней
#--------------------------

def ReadLevelProgress():
    try:
        globalvars.LevelProgress = oE.ParseDEF(File_LevelProgress).GetTag(u"MasterChef")
    except:
        oE.Log(u"Cannot read levels list")
        sys.exit()
        
#--------------------------
# Чтение глобальных настроек
#--------------------------

def ReadGameSettings():
    try:
        globalvars.CustomersInfo = {}
        globalvars.GameSettings = {}
        globalvars.PowerUpsInfo = {}
        globalvars.ThemesInfo = {}
        
        tmpGameSettings = oE.ParseDEF(File_GameSettings).GetTag(u"MasterChef")
        tmp = tmpGameSettings.GetTag(u"GameSettings").Attributes()
        while tmp.Next():
            globalvars.GameSettings[tmp.Name()] = eval(tmp.Value())
            
        #информация о покупателях
        tmpCustomersIterator = tmpGameSettings.GetTag(u"Customers").IterateTag(u"Customer")
        while tmpCustomersIterator.Next():
            tmp = tmpCustomersIterator.Get()
            globalvars.CustomersInfo[tmp.GetStrAttr(u"type")] = {
                "src": tmp.GetStrAttr(u"src"),
                "hilight": tmp.GetStrAttr(u"hilight"),
                "animation": tmp.GetStrAttr(u"animation"),
                "heartsOnStart": tmp.GetIntAttr(u"heartsOnStart"),
                "orderingTimeMin": tmp.GetFltAttr(u"orderingTimeMin"),
                "orderingTimeMax": tmp.GetFltAttr(u"orderingTimeMax"),
                "gotGiftTimeMin": tmp.GetFltAttr(u"gotGiftTimeMin"),
                "gotGiftTimeMax": tmp.GetFltAttr(u"gotGiftTimeMax"),
                "patientTimeMin": tmp.GetFltAttr(u"patientTimeMin"),
                "patientTimeMax": tmp.GetFltAttr(u"patientTimeMax"),
                "thankYouTime": tmp.GetFltAttr(u"thankYouTime"),
                "goAwayTime": tmp.GetFltAttr(u"goAwayTime"),
                "tips": eval(tmp.GetStrAttr(u"tips")),
                "takesIncompleteOrder": tmp.GetBoolAttr(u"takesIncompleteOrder"),
                "allowsExcessIngredients": tmp.GetBoolAttr(u"allowsExcessIngredients"),
                "likes": tmp.GetStrAttr(u"likes"),
                "dislikes": tmp.GetStrAttr(u"dislikes"),
            }
            
        #информация о повер-апах
        tmpPowerUpsIterator = tmpGameSettings.GetTag(u"PowerUps").IterateTag(u"PowerUp")
        while tmpPowerUpsIterator.Next():
            tmp = tmpPowerUpsIterator.Get()
            globalvars.PowerUpsInfo[tmp.GetStrAttr(u"type")] = {
                "symbol": tmp.GetStrAttr(u"symbol"),
                "price": tmp.GetIntAttr(u"price"),
            }
                
        #информация о темах
        tmpThemesIterator = tmpGameSettings.GetTag(u"Themes").IterateTag(u"Theme")
        while tmpThemesIterator.Next():
            tmp = tmpThemesIterator.Get()
            globalvars.ThemesInfo[tmp.GetStrAttr(u"type")] = {}
            for tmpKey in ["background", "counter", "customersQuePointer", "station",
                           "recipeInfo", "field", "storage", "bonuspane",
                           "trashcan", "trashcanBarEmpty", "trashcanBarFull", "tablet"]:
                globalvars.ThemesInfo[tmp.GetStrAttr(u"type")][tmpKey] = tmp.GetStrAttr(unicode(tmpKey))
        
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
        
        ##override global game settings
        #if globalvars.LevelSettings.GetCountTag(u"GameSettings") == 1:
        #    tmp = globalvars.LevelSettings.GetTag(u"GameSettings").Attributes()
        #    while tmp.Next():
        #        globalvars.GameSettings[tmp.Name()] = eval(tmp.Value())
                
        ##override customer settings
        #if tmpLevelData.GetCountTag(u"Customers") == 1:
        #    tmpCustomersIterator = tmpLevelData.GetTag(u"Customers").IterateTag(u"Customer")
        #    while tmpCustomersIterator.Next():
        #        tmpCustomer = tmpCustomersIterator.Get()
        #        tmpType = tmpCustomer.GetStrAttr(u"type")
        #        tmp = tmpCustomer.Attributes()
        #        while tmp.Next():
        #            if tmp.Name() in [u"likes", u"dislikes"]:
        #                globalvars.CustomersInfo[tmpType][tmp.Name()] = tmp.Value()
        #            elif tmp.Name() not in [u"type", u"src"]:
        #                globalvars.CustomersInfo[tmpType][tmp.Name()] = eval(tmp.Value())
                
            
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
        
    
    
    

