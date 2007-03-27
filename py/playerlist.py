#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
РЈРїСЂР°РІР»РµРЅРёРµ РїСЂРѕС„РёР»СЏРјРё Рё СЃРїРёСЃРєРѕРј РёРіСЂРѕРєРѕРІ
"""

import os, os.path
import sys
import scraft
from scraft import engine as oE
from configconst import *
from strings import *
import config
import defs
import globalvars
import string, traceback

class Player:
    #создает пустой профиль игрока
    def __init__(self):
        self.Name = ""
        self.Level = None       #указывает на ноду уровня в LevelProgress
        self.Filename = ""
        try:
            self.XML = oE.ParseDEF(File_DummyProfile).GetTag(u"MasterChef")
        except:
            oE.Log(unicode("Cannot create player profile"))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
            
    #считывает профиль игрока из файла
    def Read(self, name=""):
        self.Name = name
        self.Level = None
        self.Filename = ""
        try:
            #filename = globalvars.PlayerList.Players[name]
            #self.Filename = filename
            #self.XML = oE.ParseDEF(filename).GetTag(u"MasterChef")
            if name != "":
                filename = globalvars.PlayerList.Players[name]
                self.Filename = filename
                if config.FileValid(filename):
                    self.XML = oE.ParseDEF(filename).GetTag(u"MasterChef")
                else:
                    self.XML = oE.ParseDEF(File_DummyProfile).GetTag(u"MasterChef")
            else:
                self.XML = oE.ParseDEF(File_DummyProfile).GetTag(u"MasterChef")
        except:
            self.XML = oE.ParseDEF(File_DummyProfile).GetTag(u"MasterChef")
            #oE.Log(unicode("Cannot read player info for "+name+", empty profile is used"))
            #oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            
    #сохраняет профиль игрока в файл
    def Save(self):
        try:
            if self.Filename != "":
                self.XML.GetRoot().StoreTo(self.Filename)
        except:
            oE.Log(unicode("Cannot save player info for "+self.Name))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    #указатель на последний открытый уровень
    def LastUnlockedLevel(self):
        tmpLevel = None
        tmpIterator = self.XML.GetTag(u"Levels").IterateTag(u"level")
        while tmpIterator.Next():
            tmp = tmpIterator.Get()
            if tmp.GetBoolAttr(u"unlocked"):
                tmpLevel = tmp
        return tmpLevel
        
    def SetLevel(self, level):
        self.Level = level
        
    def GetLevel(self):
        return self.Level
        
    def GetLevelParams(self, level):
        return defs.GetTagWithContent(self.XML.GetTag(u"Levels"), u"level", level)#.Clone()
        
    def SetLevelParams(self, level, params):
        pass
        
        
class PlayerList:
    def __init__(self):
        self.Players = {}  #хранит список игроков и их файлов
        try:
            self.XML = oE.ParseDEF(File_PlayersConfig).GetTag(u"MasterChef")
        except:
            oE.Log(unicode("Cannot create players list"))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    #считывает и парсит список игроков (в начале игры)
    def Read(self):
        try:
            if config.FileValid(File_PlayersConfig):
                PlayersIterator = oE.ParseDEF(File_PlayersConfig).GetTag(u"MasterChef").IterateTag(u"player")
                while PlayersIterator.Next():
                    tmpPl = PlayersIterator.Get()
                    self.Players[tmpPl.GetContent()] = tmpPl.GetStrAttr(u"file")
            globalvars.CurrentPlayer = Player()
            globalvars.CurrentPlayer.Read(globalvars.GameConfig["Player"])
        except:
            oE.Log(u"Cannot read players list")
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    def Save(self):
        try:
            tmpSaveStr = "MasterChef {\n"
            for tmp in globalvars.PlayerList.Players.items():
                if tmp[0] != "Create new player":
                    tmpSaveStr += ("  player(" + tmp[0] + ") { file = '" + tmp[1] + "' }\n")
            tmpSaveStr += "}\n"
            config.SignAndSave(File_PlayersConfig, tmpSaveStr)
        except:
            oE.Log(u"Cannot save players list")
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
        
    #возвращает список игроков для диалогов
    def GetPlayerList(self):
        return [Str_Players_Create]+self.Players.keys()
        
    def CreatePlayer(self, name):
        try:
            filename = u"data/"+name+".def"
            self.Players[name] = filename
            self.Save()
            globalvars.CurrentPlayer = Player()
            globalvars.CurrentPlayer.Read(name)
            globalvars.CurrentPlayer.Save()
        except:
            oE.Log(unicode("Cannot create player "+name))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    def DelPlayer(self, name):
        try:
            if os.path.exists(self.Players[name]):
                os.remove(self.Players[name])
            del self.Players[name]
            self.Save()
            if globalvars.GameConfig["Player"] == name:
                globalvars.GameConfig["Player"] = ""
                config.SaveGameConfig()
                globalvars.CurrentPlayer = Player()
        except:
            oE.Log(unicode("Cannot remove player "+name))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            #sys.exit()
        
    #выбор игрока по номеру из списка
    def SelectPlayer(self, no):
        try:
            #name = self.Players.keys()[no-1]
            name = self.GetPlayerList()[no]
            globalvars.GameConfig["Player"] = name
            config.SaveGameConfig()
            globalvars.CurrentPlayer.Read(name)
        except:
            oE.Log(unicode("Cannot select player "+str(no)))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
