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

def ReadPlayers():
    """ Reads players list """
    globalvars.PlayerList = {}
    globalvars.PlList = []
    globalvars.PlayerList["Create new player"] = ""
    globalvars.PlList.append(u"Create new player")
    if config.FileValid(File_PlayersConfig):
        Data_Players = oE.ParseDEF(File_PlayersConfig)
        PlayersIterator = Data_Players.GetTag(u"unit").IterateTag(u"player")
        PlayersIterator.Reset()
        while PlayersIterator.Next():
            tmpPl = PlayersIterator.Get()
            globalvars.PlayerList[tmpPl.GetContent()] = \
                { "File": tmpPl.GetStrAttr(u"file"), "Level": tmpPl.GetIntAttr(u"level") }
            globalvars.PlList.append(tmpPl.GetContent())
    if unicode(globalvars.GameConfig["Player"]) != u'None':
        ReadPlayer(globalvars.GameConfig["Player"])

def ReadPlayer(name):
    """ Reads player parameters """
    globalvars.CurrentPlayer = {}
    globalvars.CurrentPlayer["Name"] = name
    filename = globalvars.PlayerList[name]["File"]
    if config.FileValid(filename):
        tmpNode = oE.ParseDEF(filename).GetTag(u"unit")
        globalvars.CurrentPlayer["Playing"] = tmpNode.GetBoolAttr(u"Playing")
        globalvars.CurrentPlayer["Game"] = tmpNode.GetBoolAttr(u"Game")
        if globalvars.CurrentPlayer["Game"]:
            globalvars.CurrentPlayer["GlobalScore"] = tmpNode.GetIntAttr(u"GlobalScore")
            globalvars.CurrentPlayer["LevelScore"] = tmpNode.GetIntAttr(u"LevelScore")
            globalvars.CurrentPlayer["Level"] = tmpNode.GetIntAttr(u"Level")
            globalvars.CurrentPlayer["Lives"] = tmpNode.GetIntAttr(u"Lives")
            globalvars.CurrentPlayer["Time"] = tmpNode.GetIntAttr(u"Time")
            globalvars.CurrentPlayer["InventoryDea"] = tmpNode.GetIntAttr(u"InventoryDea")
            globalvars.CurrentPlayer["InventoryBrd"] = tmpNode.GetIntAttr(u"InventoryBrd")
            globalvars.CurrentPlayer["InventoryClk"] = tmpNode.GetIntAttr(u"InventoryClk")
            globalvars.CurrentPlayer["InventoryDyn"] = tmpNode.GetIntAttr(u"InventoryDyn")
    else:
        tmpNode = oE.ParseDEF(File_DummyProfile).GetTag(u"unit")
        globalvars.CurrentPlayer["Playing"] = tmpNode.GetBoolAttr(u"Playing")
        globalvars.CurrentPlayer["Game"] = tmpNode.GetBoolAttr(u"Game")

def SavePlayers():
    """ Saves players list """
    tmpSaveStr = "unit {\n"
    for tmp in globalvars.PlayerList.items():
        if tmp[0] != "Create new player":
            tmpSaveStr += ("  player(" + tmp[0] + ") { file = '" + tmp[1]["File"] + \
                    "' level = " + str(tmp[1]["Level"]) + " }\n")
    tmpSaveStr += "}\n"
    config.SignAndSave(File_PlayersConfig, tmpSaveStr)

def NewPlayer(name):
    """ Creates new player """
    f = file(File_DummyProfile, "r")
    tmpstr = f.readlines()
    f.close()
    if not os.access("data", os.W_OK):
        os.mkdir("data")
    filename = u"data/"+name+".tpl"
    f = file(filename, "wt")
    f.writelines(tmpstr)
    f.close()
    globalvars.PlayerList[name] = { "File": filename, "Level": 0 }
    globalvars.PlList.append(name)
    SavePlayers()
    globalvars.GameConfig["Player"] = name
    config.SaveGameConfig()

def DelPlayer(name):
    """ Deletes player """
    globalvars.PlList.remove(name)
    os.remove(globalvars.PlayerList[name]["File"])
    del globalvars.PlayerList[name]
    SavePlayers()
    if globalvars.GameConfig["Player"] == name:
        globalvars.GameConfig["Player"] = 'None'
        config.SaveGameConfig()
    
def ResetPlayer():
    globalvars.CurrentPlayer["Game"] = True
    globalvars.CurrentPlayer["GlobalScore"] = NewGame_Score
    globalvars.CurrentPlayer["LevelScore"] = NewLevel_Score
