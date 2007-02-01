#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Чтение данных о рецептах, конфигураций уровней
"""

import sys
import string
import scraft
from scraft import engine as oE
import globalvars
from configconst import File_Cuisine, File_GameSettings, File_ResourceInfo, File_Animations

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
                        "fps": tmpSQ.GetIntAttr(u"fps"), "loops": tmpSQ.GetIntAttr(u"loops") }
                
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
                "type": tmp.GetStrAttr(u"type"), "src": tmp.GetStrAttr(u"src") }
            
        tmpRecipesIterator = tmpCuisineData.GetTag(u"Recipes").IterateTag(u"Recipe")
        while tmpRecipesIterator.Next():
            tmp = tmpRecipesIterator.Get()
            globalvars.CuisineInfo["Recipes"][tmp.GetStrAttr(u"name")] = {
                "type": tmp.GetStrAttr(u"type"),
                "src": tmp.GetStrAttr(u"src"),
                "price": tmp.GetIntAttr(u"price"),
                "readyAt": tmp.GetIntAttr(u"readyAt"),
                "requires": eval(tmp.GetStrAttr(u"requires"))
            }
        
    except:
        oE.Log(u"Cannot read cuisine info")
        sys.exit()

#--------------------------
# Чтение глобальных настроек
#--------------------------

def ReadGameSettings():
    try:
        globalvars.CustomersInfo = {}
        globalvars.GameSettings = {}
        globalvars.PowerUpsInfo = {}
        
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
                "animation": tmp.GetStrAttr(u"animation"),
                "heartsOnStart": tmp.GetIntAttr(u"heartsOnStart"),
                "orderingTimeMin": tmp.GetFltAttr(u"orderingTimeMin"),
                "orderingTimeMax": tmp.GetFltAttr(u"orderingTimeMax"),
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
                "src": tmp.GetStrAttr(u"src"),
                "buttonSrc": tmp.GetStrAttr(u"buttonSrc"),
                "price": tmp.GetIntAttr(u"price"),
            }
                
        
    except:
        oE.Log(u"Cannot read global game settings")
        #sys.exit()
        
#------------------------
# Чтение настроек уровня
#------------------------

def ReadLevelSettings(filename):
    try:
        globalvars.LevelSettings = {}
        globalvars.LevelInfo = { "CustomerRates": {}, "IngredientRates": {}, "RecipeRates": {} }
        globalvars.Layout = {}
        ReadGameSettings()
        
        tmpLevelData = oE.ParseDEF(unicode(filename)).GetTag(u"Level")
        
        #override global game settings
        if tmpLevelData.GetCountTag(u"GameSettings") == 1:
            tmp = tmpLevelData.GetTag(u"GameSettings").Attributes()
            while tmp.Next():
                globalvars.GameSettings[tmp.Name()] = eval(tmp.Value())
                
        #override customer settings
        if tmpLevelData.GetCountTag(u"Customers") == 1:
            tmpCustomersIterator = tmpLevelData.GetTag(u"Customers").IterateTag(u"Customer")
            while tmpCustomersIterator.Next():
                tmpCustomer = tmpCustomersIterator.Get()
                tmpType = tmpCustomer.GetStrAttr(u"type")
                tmp = tmpCustomer.Attributes()
                while tmp.Next():
                    if tmp.Name() in [u"likes", u"dislikes"]:
                        globalvars.CustomersInfo[tmpType][tmp.Name()] = tmp.Value()
                    elif tmp.Name() not in [u"type", u"src"]:
                        globalvars.CustomersInfo[tmpType][tmp.Name()] = eval(tmp.Value())
                
        #read level settings
        tmp = tmpLevelData.GetTag(u"LevelSettings").Attributes()
        while tmp.Next():
            globalvars.LevelSettings[tmp.Name()] = eval(tmp.Value())
            
        #read cutomer, recipe and ingredient rates
        for tmpKey in ["Recipe", "Customer", "Ingredient"]:
            tmpRatesKey = tmpKey+"Rates"
            tmpIterator = tmpLevelData.GetTag(unicode(tmpRatesKey)).IterateTag(unicode(tmpKey))
            while tmpIterator.Next():
                tmp = tmpIterator.Get()
                globalvars.LevelInfo[tmpRatesKey][tmp.GetStrAttr(u"type")] = tmp.GetIntAttr(u"rate")
            
        #read level layout
        tmpLayout = tmpLevelData.GetTag(u"Layout")
        globalvars.Layout["Theme"] = tmpLayout.GetStrAttr(u"theme")
        
        tmpGameBoard = tmpLayout.GetTag(u"Field")
        globalvars.Layout["Field"] = {}
        for tmpKey in ["XSize", "YSize", "X0", "Y0"]:
            globalvars.Layout["Field"][tmpKey] = tmpGameBoard.GetIntAttr(unicode(tmpKey))
            
        globalvars.Layout["Stores"] = []
        tmpCustomerStations = tmpLayout.IterateTag(u"Store")
        while tmpCustomerStations.Next():
            tmpCS = tmpCustomerStations.Get()
            globalvars.Layout["Stores"].append({
                "XSize": tmpCS.GetIntAttr(u"XSize"), "YSize": tmpCS.GetIntAttr(u"YSize"),
                "X0": tmpCS.GetIntAttr(u"X0"), "Y0": tmpCS.GetIntAttr(u"Y0") })
            
        globalvars.Layout["CustomerStations"] = []
        tmpCustomerStations = tmpLayout.IterateTag(u"CustomerStation")
        while tmpCustomerStations.Next():
            tmpCS = tmpCustomerStations.Get()
            globalvars.Layout["CustomerStations"].append({ "type": tmpCS.GetStrAttr(u"type"),
                "x": tmpCS.GetIntAttr(u"x"), "y": tmpCS.GetIntAttr(u"y"),
                "occupied": tmpCS.GetBoolAttr(u"occupied") })
            
        globalvars.Layout["PowerUps"] = []
        tmpPowerUps = tmpLayout.IterateTag(u"PowerUp")
        while tmpPowerUps.Next():
            tmpPU = tmpPowerUps.Get()
            globalvars.Layout["PowerUps"].append({ "type": tmpPU.GetStrAttr(u"type"),
                "x": tmpPU.GetIntAttr(u"x"), "y": tmpPU.GetIntAttr(u"y")})
            
        globalvars.Layout["Decorations"] = []
        tmpDecorations = tmpLayout.IterateTag(u"Decoration")
        while tmpDecorations.Next():
            tmpDeco = tmpDecorations.Get()
            globalvars.Layout["Decorations"].append({ "type": tmpDeco.GetStrAttr(u"type"),
                "x": tmpDeco.GetIntAttr(u"x"), "y": tmpDeco.GetIntAttr(u"y"),
                "layer": tmpCS.GetIntAttr(u"layer") })
            
            
    except:
        oE.Log(u"Cannot read level info from: "+filename)
        sys.exit()
        



