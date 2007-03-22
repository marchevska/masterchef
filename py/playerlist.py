#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Управление профилями и списком игроков
"""

import os
import sys
import scraft
from scraft import engine as oE
from configconst import *
import config
import globalvars
import string, traceback

def ReadPlayers():
    """ Reads players list """
    try:
        globalvars.PlayerList = {}
        globalvars.PlList = []
        globalvars.PlayerList["Create new player"] = ""
        globalvars.PlList.append(u"Create new player")
        if config.FileValid(File_PlayersConfig):
            Data_Players = oE.ParseDEF(File_PlayersConfig)
            PlayersIterator = Data_Players.GetTag(u"MasterChef").IterateTag(u"player")
            PlayersIterator.Reset()
            while PlayersIterator.Next():
                tmpPl = PlayersIterator.Get()
                globalvars.PlayerList[tmpPl.GetContent()] = tmpPl.GetStrAttr(u"file")
                globalvars.PlList.append(tmpPl.GetContent())
        if unicode(globalvars.GameConfig["Player"]) != u'None':
            ReadPlayer(globalvars.GameConfig["Player"])
    except:
        oE.Log(u"Cannot read players list")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()

def ReadPlayer(name):
    """ Reads player parameters """
    try:
        globalvars.CurrentPlayer = {"Name": name, "Level": ""}
        filename = globalvars.PlayerList[name]
        if config.FileValid(filename):
            globalvars.CurrentPlayerXML = oE.ParseDEF(filename).GetTag(u"MasterChef")
        else:
            globalvars.CurrentPlayerXML = oE.ParseDEF(File_DummyProfile).GetTag(u"MasterChef")
    except:
        oE.Log(unicode("Cannot read player info for "+name))
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()

def SavePlayers():
    """ Saves players list """
    try:
        tmpSaveStr = "MasterChef {\n"
        for tmp in globalvars.PlayerList.items():
            if tmp[0] != "Create new player":
                tmpSaveStr += ("  player(" + tmp[0] + ") { file = '" + tmp[1] + "' }\n")
        tmpSaveStr += "}\n"
        config.SignAndSave(File_PlayersConfig, tmpSaveStr)
    except:
        oE.Log(u"Cannot save players list")
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()

def NewPlayer(name):
    """ Creates new player """
    try:
        f = file(File_DummyProfile, "r")
        tmpstr = f.readlines()
        f.close()
        if not os.access("data", os.W_OK):
            os.mkdir("data")
        filename = u"data/"+name+".def"
        f = file(filename, "wt")
        f.writelines(tmpstr)
        f.close()
        globalvars.PlayerList[name] = filename
        globalvars.PlList.append(name)
        SavePlayers()
        globalvars.GameConfig["Player"] = name
        config.SaveGameConfig()
        ReadPlayer(name)
    except:
        oE.Log(unicode("Cannot create player "+name))
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()

def DelPlayer(name):
    """ Deletes player """
    try:
        globalvars.PlList.remove(name)
        os.remove(globalvars.PlayerList[name]["File"])
        del globalvars.PlayerList[name]
        SavePlayers()
        if globalvars.GameConfig["Player"] == name:
            globalvars.GameConfig["Player"] = 'None'
            config.SaveGameConfig()
    except:
        oE.Log(unicode("Cannot create player "+name))
        oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        sys.exit()
    
def ResetPlayer():
    globalvars.CurrentPlayer["Game"] = True
    globalvars.CurrentPlayer["GlobalScore"] = NewGame_Score
    globalvars.CurrentPlayer["LevelScore"] = NewLevel_Score
