#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Опции, рекорды, лучшие результаты
"""

import sys, traceback
import string
import scraft
from scraft import engine as oE
from configconst import *
from guiconst import *
import globalvars
import playerlist
import md5
import os.path

#------------------------------------------
# Функции для работы с файлом конфигурации 
#------------------------------------------

def ReadGameConfig():
    try:
        globalvars.GameConfig = {}
        if FileValid(File_GameConfig):
            tmpNode = oE.ParseDEF(File_GameConfig).GetTag(u"MasterChef")
        else:
            tmpNode = oE.ParseDEF(File_GameConfigSafe).GetTag(u"MasterChef")
        globalvars.GameConfig["Player"] = tmpNode.GetStrAttr(u"Player")
        globalvars.GameConfig["Fullscreen"] = tmpNode.GetBoolAttr(u"Fullscreen")
        globalvars.GameConfig["Mute"] = tmpNode.GetBoolAttr(u"Mute")
        globalvars.GameConfig["Hints"] = tmpNode.GetBoolAttr(u"Hints")
        globalvars.GameConfig["Sound"] = tmpNode.GetIntAttr(u"Sound")
        globalvars.GameConfig["Music"] = tmpNode.GetIntAttr(u"Music")
    except:
        oE.Log(u"Cannot read game configuration files")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()

def SaveGameConfig():
    try:
        tmpSaveStr = ""
        tmpSaveStr += "MasterChef{\n"
        tmpSaveStr += "  Player = '" + globalvars.GameConfig["Player"] + "'\n"
        tmpSaveStr += "  Mute = " + str(globalvars.GameConfig["Mute"]) + "\n"
        tmpSaveStr += "  Hints = " + str(globalvars.GameConfig["Hints"]) + "\n"
        tmpSaveStr += "  Fullscreen = " + str(globalvars.GameConfig["Fullscreen"]) + "\n"
        tmpSaveStr += "  Sound = " + str(globalvars.GameConfig["Sound"]) + "\n"
        tmpSaveStr += "  Music = " + str(globalvars.GameConfig["Music"]) + "\n}\n"
        SignAndSave(File_GameConfig, tmpSaveStr)
    except:
        oE.Log(u"Cannot write game configuration files")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()
    
def ApplyOptions():
    oE.fullscreen = globalvars.GameConfig["Fullscreen"]
    oE.PlaceWindowAt(scraft.PositionCenter)
    if globalvars.GameConfig["Mute"]:
        oE.volume = 0
    else:
        oE.volume = 100
    oE.SetChannelVolume(Channel_Music, globalvars.GameConfig["Music"])    
    oE.SetChannelVolume(Channel_Time, globalvars.GameConfig["Sound"])    
    oE.SetChannelVolume(Channel_Default, globalvars.GameConfig["Sound"])    

#--------------------------------
# Функции для работы с hiscrores
#--------------------------------

def ReadHiscores():
    """ Reads hiscores list """
    globalvars.HiscoresList = []
    if FileValid(File_Hiscores):
        Data_Hiscores = oE.ParseDEF(File_Hiscores)
        HiscoresIterator = Data_Hiscores.GetTag(u"MasterChef").IterateTag(u"score")
        HiscoresIterator.Reset()
        while HiscoresIterator.Next():
            tmpScore = HiscoresIterator.Get()
            globalvars.HiscoresList.append({ "Name": tmpScore.GetStrAttr(u"Name"), \
                                            "Score": tmpScore.GetIntAttr(u"Score"),
                                            "Active": False })
    UpdateHiscores()

def SaveHiscores():
    """ Saves hiscores list """
    tmpSaveStr = ""
    tmpSaveStr += "MasterChef{\n"
    for tmp in globalvars.HiscoresList:
        tmpSaveStr += ("  score() { Name = '" + tmp["Name"] + \
                    "' Score = " + str(tmp["Score"]) + " }\n")
    tmpSaveStr += "}\n"
    SignAndSave(File_Hiscores, tmpSaveStr)

def UpdateHiscores():
    globalvars.HiscoresList.sort(lambda x,y: cmp(y["Score"], x["Score"]))
    if len(globalvars.HiscoresList) > Max_Scores:
        for i in range(Max_Scores, len(globalvars.HiscoresList)):
            del globalvars.HiscoresList[-1]

def ClearHiscores():
    globalvars.HiscoresList = []
    SaveHiscores()
    
def IsInHiscores(score):
    if len(globalvars.HiscoresList) < Max_Scores:
        return True
    elif score > globalvars.HiscoresList[-1]["Score"]:
        return True
    else:
        return False
    
def AddScore():
    for tmp in globalvars.HiscoresList:
        tmp["Active"] = False
    globalvars.HiscoresList.append({ "Name": globalvars.CurrentPlayer["Name"], \
                                    "Score": globalvars.CurrentPlayer["GlobalScore"], "Active": True })
    UpdateHiscores()

#--------------------------------------
# Функции для работы с файлом рекордов 
#--------------------------------------

def ReadBestResults():
    globalvars.BestResults = {}
    if FileValid(File_BestResults):
        BestResults_Iterator = oE.ParseDEF(File_BestResults).GetTag(u"MasterChef").IterateTag(u"level")
        BestResults_Iterator.Reset()
        while BestResults_Iterator.Next():
            tmpResult = BestResults_Iterator.Get()
            globalvars.BestResults[eval(tmpResult.GetContent())] = {
                "BestTime": tmpResult.GetIntAttr(u"BestTime"), 
                "PlayerTime": tmpResult.GetStrAttr(u"PlayerTime"), 
                "BestScore": tmpResult.GetIntAttr(u"BestScore"), 
                "PlayerScore": tmpResult.GetStrAttr(u"PlayerScore") }

def SaveBestResults():
    tmpSaveStr = ""
    tmpSaveStr += "MasterChef{\n"
    for key in globalvars.BestResults.keys():
        tmp = globalvars.BestResults[key]
        tmpSaveStr += ("  level(" + str(key) + ") { BestTime = " + str(tmp["BestTime"]) + \
                " PlayerTime = '" + tmp["PlayerTime"] + "'" + \
                " BestScore = " + str(tmp["BestScore"]) + \
                " PlayerScore = '" + tmp["PlayerScore"] + "' }\n")
    tmpSaveStr += "}\n"
    SignAndSave(File_BestResults, tmpSaveStr)

def UpdateBestResults(level, name, score, time):
    if globalvars.BestResults.has_key(level):
        if globalvars.BestResults[level]["BestTime"] >= time:
            globalvars.BestResults[level]["BestTime"] = time 
            globalvars.BestResults[level]["PlayerTime"] = name
        if globalvars.BestResults[level]["BestScore"] <= score:
            globalvars.BestResults[level]["BestScore"] = score 
            globalvars.BestResults[level]["PlayerScore"] = name
    else:
        globalvars.BestResults[level] = { "BestTime": time, "PlayerTime": name,
                                        "BestScore": score, "PlayerScore": name }
    SaveBestResults()

#---------------------------
# Проверка валидности файла
# Сохранение файла
#---------------------------

def FileValid(filename):
    try:
        f = file(filename, "rt")
        return True
        #tmpStr = f.read()
        #f.close()
        #tmpPos = string.rfind(tmpStr, Str_SignatureBegin)
        #tmpPos2 = string.rfind(tmpStr, Str_SignatureEnd)
        #tmpStrData = tmpStr[0:tmpPos]
        #tmpSign = tmpStr[tmpPos+len(Str_SignatureBegin):tmpPos2]
        #tmpRealSign = Hexy(md5.new(tmpStrData).digest())
        #if tmpSign == tmpRealSign:
        #    return True
        #else:
        #    return False
    except:
        return False

def SignAndSave(filename, str):
    tmpSaveData = str
    #tmpDir = os.path.dirname(filename)
    #if not os.access(tmpDir, os.W_OK):
    #    os.mkdir(tmpDir)
    #tmpHashStr = Hexy(md5.new(str).digest())
    #tmpSaveData = str + Str_SignatureBegin + tmpHashStr + Str_SignatureEnd
    f = file(filename, "w")
    f.write(tmpSaveData)
    f.close()
 
def Hexy(str):
    hexy = ""
    for sym in str:
        hexy += hex(ord(sym))
    return hexy    
