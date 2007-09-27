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
# найти каталог для записи данных -
# либо в Application Data, лио рядом с игрой
#------------------------------------------
def GetFileLocations():
    globalvars.DataDirectory = oE.rscpath + Str_DataDirectory
    globalvars.CheckDirs = [globalvars.DataDirectory]
    try:
        tmp = os.getenv("APPDATA", "")
        if tmp != "":
            globalvars.DataDirectory = tmp + "\\" + Str_DeveloperDirectory + "\\" + Str_ProductDirectory + "\\" + Str_DataDirectory
            globalvars.CheckDirs  = [tmp + "\\" + Str_DeveloperDirectory,
                                    tmp + "\\" + Str_DeveloperDirectory + "\\" + Str_ProductDirectory,
                                    tmp + "\\" + Str_DeveloperDirectory + "\\" + Str_ProductDirectory + "\\" + Str_DataDirectory]
    except:
        pass
    
    globalvars.File_GameConfig = globalvars.DataDirectory + File_GameConfigName
    globalvars.File_Hiscores = globalvars.DataDirectory + File_HiscoresName
    globalvars.File_BestResults = globalvars.DataDirectory + File_BestResultsName
    globalvars.File_PlayersConfig = globalvars.DataDirectory + File_PlayersConfigName
    
    globalvars.File_HiscoresSafe = oE.rscpath + File_HiscoresSafeName
    globalvars.File_PlayersConfigSafe = oE.rscpath + File_PlayersConfigSafeName
    globalvars.File_DummyProfile = oE.rscpath + File_DummyProfileName
    globalvars.File_GameConfigSafe = oE.rscpath + File_GameConfigSafeName
    globalvars.File_BestResultsSafe = oE.rscpath + File_BestResultsSafeName

    globalvars.File_Hints = oE.rscpath + File_HintsName
    globalvars.File_Cuisine = oE.rscpath + File_CuisineName
    globalvars.File_Recipes = oE.rscpath + File_RecipesName
    globalvars.File_GameSettings = oE.rscpath + File_GameSettingsName
    globalvars.File_ResourceInfo = oE.rscpath + File_ResourceInfoName
    globalvars.File_FontsInfo = oE.rscpath + File_FontsInfoName
    globalvars.File_Animations = oE.rscpath + File_AnimationsName
    globalvars.File_LevelProgress = oE.rscpath + File_LevelProgressName
    globalvars.File_GameTexts = oE.rscpath + File_GameTextsName

#------------------------------------------
# Функции для работы с файлом конфигурации 
#------------------------------------------

def ReadGameConfig():
    try:
        if FileValid(globalvars.File_GameConfig) and globalvars.RunMode == RunMode_Play:
            globalvars.GameConfig = oE.ParseDEF(globalvars.File_GameConfig).GetTag(DEF_Header)
        else:
            globalvars.GameConfig = oE.ParseDEF(globalvars.File_GameConfigSafe).GetTag(DEF_Header)
    except:
        oE.Log(u"Cannot read game configuration files")
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        sys.exit()

def SaveGameConfig():
    try:
        if globalvars.RunMode == RunMode_Play:
            SaveToFile(globalvars.GameConfig.GetRoot(), globalvars.File_GameConfig)
    except:
        oE.Log(u"Cannot write game configuration files")
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
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
    try:
        if FileValid(globalvars.File_Hiscores) and globalvars.RunMode == RunMode_Play:
            globalvars.Hiscores = oE.ParseDEF(globalvars.File_Hiscores).GetTag(DEF_Header)
        else:
            globalvars.Hiscores = oE.ParseDEF(globalvars.File_HiscoresSafe).GetTag(DEF_Header)
            SaveHiscores()
    except:
        oE.Log("Cannot read hiscores")
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        sys.exit()

def SaveHiscores():
    """ Saves hiscores list """
    try:
        if globalvars.RunMode == RunMode_Play:
            SaveToFile(globalvars.Hiscores.GetRoot(), globalvars.File_Hiscores)
    except:
        oE.Log("Cannot write hiscores")
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        sys.exit()

def ClearHiscores():
    try:
        globalvars.Hiscores = oE.ParseDEF(globalvars.File_HiscoresSafe).GetTag(DEF_Header)
        SaveHiscores()
    except:
        oE.Log("Clearing hiscores: cannot write hiscores")
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        sys.exit()
    
#сортировка и отсев лишних записей
def UpdateHiscores():
    try:
        for tmpTagNode in globalvars.Hiscores.Tags():
            tmpScoresList = map(lambda x: (x.GetContent(), x.GetIntAttr("score")), tmpTagNode.Tags())
            tmpScoresList.sort(lambda x,y: cmp(y[1], x[1]))
            
            #если более одного игрока имеют одинаковый результат,
            #поднять текущего игрока
            tmp = filter(lambda x: tmpScoresList[x][0] == globalvars.GameConfig.GetStrAttr("Player"),
                                          range(len(tmpScoresList)))
            if tmp == []:
                tmpCurrentNo = -1
            else:
                tmpCurrentNo = tmp[0]
                if tmpCurrentNo > 0:
                    if tmpScoresList[tmpCurrentNo-1][1] == tmpScoresList[tmpCurrentNo][1]:
                        tmpEl = tmpScoresList[tmpCurrentNo-1]
                        tmpScoresList[tmpCurrentNo-1] = tmpScoresList[tmpCurrentNo]
                        tmpScoresList[tmpCurrentNo] = tmpEl
                        tmpCurrentNo -= 1
            
            #если результат текущего игрока не входит в первые Max_Scores,
            #то поднять результат текущего игрока, чтобы он вошел в список
            if len(tmpScoresList) > Max_Scores:
                if tmpCurrentNo >= Max_Scores:
                        tmpScoresList[Max_Scores-1] = tmpScoresList[tmpCurrentNo]
                tmpScoresList = tmpScoresList[:Max_Scores]
            
            #оставить не более Max_Scores результатов
            i = 0
            for tmp in tmpTagNode.Tags():
                if i < len(tmpScoresList):
                    tmp.SetContent(tmpScoresList[i][0])
                    tmp.SetIntAttr("score", tmpScoresList[i][1])
                else:
                    tmp.Erase()
                i += 1
        SaveHiscores()
    except:
        pass

#добавить результат игрока
def AddScores(scores):
    try:
        for tmp in scores.keys():
            tmpTagNode = globalvars.Hiscores.GetSubtag(tmp)
            tmpScoreNode = tmpTagNode.GetSubtag(globalvars.GameConfig.GetStrAttr("Player"))
            if tmpScoreNode == None:
                tmpScoreNode = tmpTagNode.Insert("player")
                tmpScoreNode.SetContent(globalvars.GameConfig.GetStrAttr("Player"))
                tmpScoreNode.SetIntAttr("score", scores[tmp])
            if scores[tmp] > tmpScoreNode.GetIntAttr("score"):
                tmpScoreNode.SetIntAttr("score", scores[tmp])
    except:
        pass
    UpdateHiscores()

#--------------------------------------
# Функции для работы с файлом рекордов 
#--------------------------------------

def ReadBestResults():
    try:
        if FileValid(globalvars.File_BestResults) and globalvars.RunMode == RunMode_Play:
            globalvars.BestResults = oE.ParseDEF(globalvars.File_BestResults).GetTag(DEF_Header)
        else:
            globalvars.BestResults = oE.ParseDEF(globalvars.File_BestResultsSafe).GetTag(DEF_Header)
    except:
        oE.Log(u"Cannot read best results record")
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        sys.exit()

def SaveBestResults():
    try:
        if globalvars.RunMode == RunMode_Play:
            SaveToFile(globalvars.BestResults.GetRoot(), globalvars.File_BestResults)
    except:
        oE.Log(u"Cannot write best results record")
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        sys.exit()

def UpdateBestResults(level, name, score):
    try:
        tmp = globalvars.BestResults.GetSubtag(level)
        tmp.SetIntAttr("hiscore", score)
        tmp.SetStrAttr("player", name)
        SaveBestResults()
    except:
        oE.Log(u"Error updating best results list")
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))

#---------------------------
# Проверка валидности файла
#---------------------------
def FileValid(filename):
    try:
        if globalvars.GameSettings.GetBoolAttr("debugMode") == True and os.access(filename, os.W_OK):
            return True
        else:
            if not os.access(filename, os.W_OK):
                return False
            else:
                tmp = oE.ParseDEF(filename)
                if tmp.GetCountTag("signature") != 1:
                    return False
                elif tmp.GetTag("signature").GetContent() != Hexy(tmp):
                    return False
                else:
                    return True
    except:
        oE.Log("Validity check failed for the following file: %s"%filename)
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        return False

#---------------------------
# возвращает md5-подпись от содержимого ноды
#---------------------------
def Hexy(node):
    #подсчитать хэш записанных строк, не обращая внимания на атрибуты
    tmpSum = ""
    for tmp in [node.GetTag(DEF_Header)] + list(node.GetTag(DEF_Header).Tags()):
        tmpAttrs = list(tmp.Attributes())
        tmpAttrs.sort(lambda x,y: cmp(x[0], y[0]))
        for (name, value) in tmpAttrs:
            tmpSum += string.lower(name+value)
    str = md5.new(tmpSum).digest()
    hexy = ""
    for sym in str:
        hexy += hex(ord(sym))
    return hexy

#---------------------------
# Сохранение ноды в файл. Бехопасное и с подписью
#---------------------------
def SaveToFile(node, filename):
    try:
        for tmpDir in globalvars.CheckDirs:
            if not os.access(tmpDir, os.W_OK):
                os.mkdir(tmpDir)
        tmpFilename = filename+"$_$"
        #вставить ноду с подписью, записать файл, вырезать ноду
        if node.GetCountTag("signature") < 1:
            tmpSignNode = node.Insert("signature")
        else:
            tmpSignNode = node.GetTag("signature")
        tmpSignNode.SetContent(Hexy(node))
        node.StoreTo(tmpFilename)
        #try:
        #    tmpSignNode.Erase()
        #except:
        #    oE.Log("Error saving to file: %s"%filename)
        #    oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        if os.access(filename, os.W_OK):
            os.remove(filename)
        os.rename(tmpFilename, filename)
    except:
        oE.Log("Error saving to file: %s"%filename)
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        
