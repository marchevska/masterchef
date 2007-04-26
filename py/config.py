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
import os, os.path

#------------------------------------------
# Функции для работы с файлом конфигурации 
#------------------------------------------

def ReadGameConfig():
    try:
        if FileValid(File_GameConfig) and globalvars.RunMode == RunMode_Play:
            globalvars.GameConfig = oE.ParseDEF(File_GameConfig).GetTag(u"MasterChef")
        else:
            globalvars.GameConfig = oE.ParseDEF(File_GameConfigSafe).GetTag(u"MasterChef")
    except:
        oE.Log(u"Cannot read game configuration files")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()

def SaveGameConfig():
    try:
        if globalvars.RunMode == RunMode_Play:
            SaveToFile(globalvars.GameConfig.GetRoot(), File_GameConfig)
    except:
        oE.Log(u"Cannot write game configuration files")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()
    
def ApplyOptions():
    oE.fullscreen = globalvars.GameConfig.GetBoolAttr("Fullscreen")
    oE.PlaceWindowAt(scraft.PositionCenter)
    if globalvars.GameConfig.GetBoolAttr("Mute"):
        oE.volume = 0
    else:
        oE.volume = 100
    oE.SetChannelVolume(Channel_Music, globalvars.GameConfig.GetIntAttr("Music"))    
    oE.SetChannelVolume(Channel_Time, globalvars.GameConfig.GetIntAttr("Sound"))    
    oE.SetChannelVolume(Channel_Default, globalvars.GameConfig.GetIntAttr("Sound"))    

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
    #tmpSaveStr = ""
    #tmpSaveStr += "MasterChef{\n"
    #for tmp in globalvars.HiscoresList:
    #    tmpSaveStr += ("  score() { Name = '" + tmp["Name"] + \
    #                "' Score = " + str(tmp["Score"]) + " }\n")
    #tmpSaveStr += "}\n"
    #SignAndSave(File_Hiscores, tmpSaveStr)
    pass

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
    try:
        if FileValid(File_BestResults) and globalvars.RunMode == RunMode_Play:
            globalvars.BestResults = oE.ParseDEF(File_BestResults).GetTag(u"MasterChef")
        else:
            globalvars.BestResults = oE.ParseDEF(File_BestResultsSafe).GetTag(u"MasterChef")
    except:
        oE.Log(u"Cannot read best results record")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()

def SaveBestResults():
    try:
        if globalvars.RunMode == RunMode_Play:
            SaveToFile(globalvars.BestResults.GetRoot(), File_BestResults)
    except:
        oE.Log(u"Cannot write best results record")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()

def UpdateBestResults(level, name, score):
    try:
        tmp = globalvars.BestResults.GetSubtag(level)
        tmp.SetIntAttr("hiscore", score)
        tmp.SetStrAttr("player", name)
        SaveBestResults()
    except:
        oE.Log(u"Error updating best results list")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))

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
    tmpDir = os.path.dirname(filename)
    if not os.access(tmpDir, os.W_OK):
        os.mkdir(tmpDir)
    #tmpHashStr = Hexy(md5.new(str).digest())
    #tmpSaveData = str + Str_SignatureBegin + tmpHashStr + Str_SignatureEnd
    tmpSaveData = str
    f = file(filename, "w")
    f.write(tmpSaveData)
    f.close()
 
def Hexy(str):
    hexy = ""
    for sym in str:
        hexy += hex(ord(sym))
    return hexy

def SaveToFile(node, filename):
    try:
        tmpDir = os.path.dirname(filename)
        if not os.access(tmpDir, os.W_OK):
            os.mkdir(tmpDir)
        tmpFilename = filename+"$_$"
        node.StoreTo(tmpFilename)
        if os.access(filename, os.W_OK):
            os.remove(filename)
        os.rename(tmpFilename, filename)
    except:
        oE.Log("Error saving to file: %s"%filename)
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        
