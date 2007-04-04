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

    #------------------------------------
    #создает пустой профиль игрока
    #------------------------------------
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
            
    #------------------------------------
    # считывает профиль игрока из файла
    #------------------------------------
    def Read(self, name=""):
        self.Name = name
        self.Level = None
        self.Filename = ""
        try:
            if name != "":
                filename = globalvars.PlayerList.FilenameFor(name)
                self.Filename = filename
                if config.FileValid(filename):
                    self.XML = oE.ParseDEF(filename).GetTag(u"MasterChef")
                else:
                    self.XML = oE.ParseDEF(File_DummyProfile).GetTag(u"MasterChef")
            else:
                self.XML = oE.ParseDEF(File_DummyProfile).GetTag(u"MasterChef")
        except:
            try:
                self.XML = oE.ParseDEF(File_DummyProfile).GetTag(u"MasterChef")
            except:
                #если никак-никак не можем прочитать
                oE.Log(unicode("Cannot read player info for "+name))
                oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
                sys.exit()
            
    #------------------------------------
    # сохраняет профиль игрока в файл
    #------------------------------------
    def Save(self):
        try:
            if globalvars.RunMode == RunMode_Play and self.Filename != "":
                tmpDir = os.path.dirname(self.Filename)
                if not os.access(tmpDir, os.W_OK):
                    os.mkdir(tmpDir)
                self.XML.GetRoot().StoreTo(self.Filename)
        except:
            oE.Log(unicode("Cannot save player info for "+self.Name))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    #------------------------------------
    # указатель на последний открытый уровень или комикс - см по значению type
    #------------------------------------
    def LastUnlockedLevel(self, type = u"level"):
        tmp = filter(lambda x: x.GetBoolAttr(u"unlocked"), self.XML.Tags(type))
        if len (tmp)>0:
            return tmp[-1]
        else:
            return None
        
    #------------------------------------
    # установить текущий уровень
    #------------------------------------
    def SetLevel(self, level):
        try:
            self.Level = level#.Clone()
            tmpNode = self.XML.GetSubtag(level.GetContent())
            if level.GetName() == u"comic":
                #если комикс: отметить в профиле игрока комикс как увиденный
                tmpNode.SetBoolAttr(u"seen", True)
                #если текущий - комикс, то отметить следующий уровень или комикс как разлоченный
                if level.Next():
                    tmpNextLevel = self.XML.GetSubtag(level.Next().GetContent())
                    if tmpNextLevel.HasAttr(u"unlocked"):
                        tmpNextLevel.SetBoolAttr(u"unlocked", True)
            elif level.GetName() == u"level":
                #если уровень: отметить в профиле игрока уровень как начатый
                tmpNode.SetBoolAttr(u"played", True)
            self.Save()
        except:
            oE.Log(unicode("Cannot set level to "+level.GetContent()))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    def GetLevel(self):
        return self.Level
        
    def NextLevel(self):
        self.Level = self.Level.Next()
        
    #------------------------------------
    #возвращает ноду уровня по его имени
    #------------------------------------
    def GetLevelParams(self, level):
        return self.XML.GetSubtag(level)
        
    def SetLevelParams(self, level, params):
        pass
        
    #------------------------------------
    # записать результаты текущего уровня + в профиль тоже
    #------------------------------------
    def RecordLevelResults(self, params):
        try:
            tmpLevelNode = self.XML.GetSubtag(self.Level.GetContent())
            if globalvars.RunMode == RunMode_Play:
                if params.has_key("expert"):
                    if params["expert"]:
                        tmpLevelNode.SetBoolAttr("expert", True)
                if params.has_key("played"):
                    tmpLevelNode.SetBoolAttr("played", True)
                if params.has_key("hiscore"):
                    if params["hiscore"] > tmpLevelNode.GetIntAttr("hiscore"):
                        tmpLevelNode.SetIntAttr("hiscore", params["hiscore"])
                    #проверить, достигнута ли цель уровня; если да - разлочить следующий
                    if params["hiscore"] >= globalvars.LevelSettings["moneygoal"]:
                        tmpNextLevelNode = self.XML.GetSubtag(self.Level.Next().GetContent())
                        if tmpNextLevelNode:
                            tmpNextLevelNode.SetBoolAttr("unlocked", True)
                self.Save()
            else:
                tmpLevelNode.SetBoolAttr("unlocked", True)
        except:
            oE.Log(unicode("Cannot update player profile"))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
            
class PlayerList:
    def __init__(self):
        try:
            self.Filename = ""
            self.XML = oE.ParseDEF(File_PlayersConfigSafe).GetTag(u"MasterChef")
        except:
            oE.Log(unicode("Cannot create players list"))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    #считывает и парсит список игроков (в начале игры)
    def Read(self):
        try:
            self.Filename = File_PlayersConfig
            if config.FileValid(self.Filename):
                self.XML = oE.ParseDEF(self.Filename).GetTag(u"MasterChef")
            globalvars.CurrentPlayer = Player()
            globalvars.CurrentPlayer.Read(globalvars.GameConfig.GetStrAttr("Player"))
        except:
            try:
                self.XML = oE.ParseDEF(File_PlayersConfigSafe).GetTag(u"MasterChef")
            except:
                #если никак-никак не можем прочитать
                oE.Log(u"Cannot read players list")
                oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
                sys.exit()
        
    def Save(self):
        try:
            if self.Filename != "":
                tmpDir = os.path.dirname(self.Filename)
                if not os.access(tmpDir, os.W_OK):
                    os.mkdir(tmpDir)
                self.XML.GetRoot().StoreTo(self.Filename)
        except:
            oE.Log(u"Cannot save players list")
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            #sys.exit()
        
    #возвращает имя фала для заданного имени игрока
    def FilenameFor(self, name):
        return self.XML.Subtags(unicode(name)).Get().GetStrAttr(u"file")
        
    #возвращает список игроков для диалогов
    def GetPlayerList(self):
        return [Str_Players_Create]+[x.GetContent() for x in self.XML]
        
    def CreatePlayer(self, name):
        try:
            filename = u"data/"+name+".def"
            tmp = scraft.Xdata("player(%s) { file = '%s' }" % (name, filename)).GetTag()
            tmp.SetContent(unicode(name))
            self.XML.InsertCopyOf(tmp)
            self.Save()
            globalvars.CurrentPlayer = Player()
            globalvars.CurrentPlayer.Read(name)
            globalvars.CurrentPlayer.Save()
        except:
            oE.Log(unicode("Cannot create player "+name))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    # удаление игрока по имени
    def DelPlayer(self, name):
        try:
            if os.path.exists(self.FilenameFor(name)):
                os.remove(self.FilenameFor(name))
            self.XML.GetSubtag(name).Erase()
            self.Save()
            if globalvars.GameConfig.GetStrAttr("Player") == name:
                globalvars.GameConfig.SetStrAttr("Player", "")
                config.SaveGameConfig()
                globalvars.CurrentPlayer = Player()
        except:
            oE.Log(unicode("Cannot remove player "+name))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    #выбор игрока по номеру из списка
    def SelectPlayer(self, name):
        try:
            #name = self.GetPlayerList()[no]
            globalvars.GameConfig.SetStrAttr("Player", name)
            config.SaveGameConfig()
            globalvars.CurrentPlayer.Read(name)
        except:
            oE.Log(unicode("Cannot select player "+str(no)))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
