#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Работа со списком игроков и с профилями игроков
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
            self.XML = oE.ParseDEF(File_DummyProfile).GetTag("MasterChef")
        except:
            oE.Log("Cannot create player profile")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
            
    #------------------------------------
    # считывает профиль игрока из файла
    #------------------------------------
    def Read(self, name=""):
        self.Name = name
        self.Level = None
        self.Filename = ""
        dummyXML = oE.ParseDEF(File_DummyProfile).GetTag("MasterChef")
        try:
            if name != "":
                filename = globalvars.PlayerList.FilenameFor(name)
                self.Filename = filename
                if config.FileValid(filename):
                    self.XML = oE.ParseDEF(filename).GetTag("MasterChef")
                else:
                    self.XML = dummyXML
            else:
                self.XML = dummyXML
        except:
            try:
                self.XML = dummyXML
            except:
                #если никак-никак не можем прочитать
                oE.Log("Cannot read player info for "+name)
                oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
                sys.exit()
        #append nodes from dummy profile if necessary
        for tmpNode in dummyXML.Tags():
            tmp = self.XML.GetSubtag(tmpNode.GetContent(), tmpNode.GetName())
            if tmp == None:
                tmp = self.XML.Insert(tmpNode.GetName())
                tmp.SetContent(tmpNode.GetContent())
            for attr in ("played", "unlocked", "expert", "seen"):
                if tmpNode.HasAttr(attr) and not tmp.HasAttr(attr):
                    tmp.SetBoolAttr(attr, tmpNode.GetBoolAttr(attr))
            for attr in ("hiscore",):
                if tmpNode.HasAttr(attr) and not tmp.HasAttr(attr):
                    tmp.SetIntAttr(attr, tmpNode.GetIntAttr(attr))
        self.Save()
        
    #------------------------------------
    # сохраняет профиль игрока в файл
    #------------------------------------
    def Save(self):
        try:
            if globalvars.RunMode == RunMode_Play and self.Filename != "":
                config.SaveToFile(self.XML.GetRoot(), self.Filename)
        except:
            oE.Log("Cannot save player info for "+self.Name)
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
    #------------------------------------
    # название последнего открытого уровня
    #------------------------------------
    def LastUnlockedLevel(self, type = "level"):
        tmp = filter(lambda x: x.GetBoolAttr("unlocked"), self.XML.Tags(type))
        if len (tmp)>0:
            return tmp[-1].GetContent()
        else:
            return ""
        
    def NewUnlockedLevel(self, type = "level"):
        if self.XML.HasAttr("newUnlocked"):
            if self.XML.GetStrAttr("newUnlocked")!="":
                return self.XML.GetStrAttr("newUnlocked")
        return ""
        
    def PopNewUnlockedLevel(self):
        self.XML.SetStrAttr("newUnlocked", "")
        
    def _UnlockEntry(self, entry):
        if not entry.GetBoolAttr("unlocked") and entry.GetName() in ("comic", "intro", "outro", "level"):
            self.XML.SetStrAttr("newUnlocked", entry.GetContent())
        entry.SetBoolAttr("unlocked", True)
        
    #------------------------------------
    # установить текущий уровень
    #------------------------------------
    def SetLevel(self, level):
        try:
            self.Level = level#.Clone()
            tmpNode = self.XML.GetSubtag(level.GetContent())
            if level.GetName() in ("comic", "intro"):
                #если комикс или интро: отметить в профиле игрока уровень как увиденный
                tmpNode.SetBoolAttr("seen", True)
                #если текущий - комикс, то отметить следующий уровень или комикс как разлоченный
                if level.Next():
                    tmpNextLevel = self.XML.GetSubtag(level.Next().GetContent())
                    if tmpNextLevel.HasAttr("unlocked"):
                        self._UnlockEntry(tmpNextLevel)
                        #tmpNextLevel.SetBoolAttr("unlocked", True)
                #разлочить эпизод после интро, если необходимо
                if level.GetName() == "intro":
                    self._UnlockEntry(self.XML.GetSubtag(level.GetStrAttr("episode")))
                    #self.XML.GetSubtag(level.GetStrAttr("episode")).SetBoolAttr(u"unlocked", True)
            
            elif level.GetName() == "outro":
                #если аутро: отметить в профиле игрока уровень как увиденный
                tmpNode.SetBoolAttr("seen", True)
                #проверка экспертного прохождения всех уровней этого эпизода
                if self.XML.GetSubtag(level.GetStrAttr("episode")).GetIntAttr("points") >= \
                        globalvars.GameSettings.GetIntAttr("expertAll"):
                    tmpNode.SetBoolAttr("expert", True)
                #проверить условие для разлочивания следующего уровня
                if level.Next() and self.GetScoresPlaceAndCondition()["pass"]:
                    tmpNextLevel = self.XML.GetSubtag(level.Next().GetContent())
                    if tmpNextLevel.HasAttr("unlocked"):
                        self._UnlockEntry(tmpNextLevel)
                        #tmpNextLevel.SetBoolAttr("unlocked", True)
            
            elif level.GetName() == u"level":
                #если уровень: отметить в профиле игрока уровень как начатый
                tmpNode.SetBoolAttr(u"played", True)
            self.Save()
        except:
            oE.Log("Cannot set level to "+level.GetContent())
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
    #------------------------------------
    #проверить условие для разлочивания следующего уровня после outro
    #------------------------------------
    def GetScoresPlaceAndCondition(self):
        tmpConditions = eval(self.Level.GetStrAttr("passIf"))
        tmpPass = True
        for episode in tmpConditions.keys():
            tmpResults = eval(globalvars.LevelProgress.GetTag("People").GetSubtag(episode).GetStrAttr("people"))
            tmpResults[globalvars.GameSettings.GetStrAttr("charName")] = self.XML.GetSubtag(episode).GetIntAttr("points")
            tmp = tmpResults.items()
            tmp.sort(lambda x,y: cmp(y[1], x[1]))
            tmpPlace = tmp.index((globalvars.GameSettings.GetStrAttr("charName"),self.XML.GetSubtag(episode).GetIntAttr("points")))+1
            if tmpPlace > tmpConditions[episode]:
                tmpPass = False
        return { "scores": tmp, "place": tmpPlace, "pass": tmpPass }
        
    def GetLevel(self):
        return self.Level
        
    def NextLevel(self):
        self.Level = self.Level.Next()
        
    #------------------------------------
    #возвращает ноду уровня по его имени
    #------------------------------------
    def GetLevelParams(self, level):
        if self.XML.GetSubtag(level) != None:
            return self.XML.GetSubtag(level)
        else:
            return oE.ParseDEF(File_DummyProfile).GetTag(u"MasterChef").GetSubtag(level)
        
    def SetLevelParams(self, level, params):
        tmp = self.XML.GetSubtag(level)
        for attr in ("played", "unlocked", "expert", "seen"):
            if params.has_key(attr):
                tmp.SetBoolAttr(attr, params[attr])
        for attr in ("hiscore",):
            if params.has_key(attr):
                tmp.SetIntAttr(attr, params[attr])
        self.Save()
        
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
                    #проверить, достигнута ли цель уровня; 
                    #если да - разлочить следующий и разлочить рецепты
                    if params["hiscore"] >= globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("moneyGoal"):
                        tmpNextLevelNode = self.XML.GetSubtag(self.Level.Next().GetContent())
                        if tmpNextLevelNode:
                            self._UnlockEntry(tmpNextLevelNode)
                            #tmpNextLevelNode.SetBoolAttr("unlocked", True)
                        tmpRecipes = eval(self.Level.GetStrAttr("unlock"))
                        for rcp in tmpRecipes:
                            self._UnlockEntry(self.XML.GetSubtag(rcp))
                            #self.XML.GetSubtag(rcp).SetBoolAttr("unlocked", True)
            else:
                self._UnlockEntry(tmpLevelNode)
                #tmpLevelNode.SetBoolAttr("unlocked", True)
                
            #сосчитать и записать суммарные результаты по всем уровням
            #за простое прохождение уровня - 5 очков, за экспертное - 10
            for tmp in globalvars.LevelProgress.GetTag("Levels").Tags("outro"):
                #tmpSum = reduce(lambda x,y: x+y,
                #    map(lambda x: self.XML.GetSubtag(x).GetIntAttr("hiscore"), eval(tmp.GetStrAttr("sum"))))
                tmpSum = reduce(lambda x,y: x+y,
                        map(lambda x: (x.GetBoolAttr("expert"))*globalvars.GameSettings.GetIntAttr("expertPoints")+\
                        (x.GetIntAttr("hiscore")>0 and not x.GetBoolAttr("expert"))*globalvars.GameSettings.GetIntAttr("levelPoints"),
                        map(lambda y: self.XML.GetSubtag(y), eval(tmp.GetStrAttr("sum")))))
                self.XML.GetSubtag(tmp.GetStrAttr("episode")).SetIntAttr("points", tmpSum)
            self.Save()
        except:
            oE.Log("Cannot update player profile")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
    #------------------------------------
    # возвращает список вновь открытых, но еще
    #не показанных рецептов в текущем сеттинге
    #------------------------------------
    def JustUnlockedRecipes(self, setting):
        tmpRecipes = filter(lambda x: globalvars.RecipeInfo.GetSubtag(x).GetStrAttr("setting") == setting,
                                map(lambda x: x.GetContent(), globalvars.RecipeInfo.Tags()))
        return filter(lambda x: self.GetLevelParams(x).GetBoolAttr("unlocked") == True and
                    self.GetLevelParams(x).GetBoolAttr("seen") == False,
                    tmpRecipes)
            
#------------------------------------
# управление списком игроков
#------------------------------------
class PlayerList:
    def __init__(self):
        try:
            self.Filename = ""
            self.XML = oE.ParseDEF(File_PlayersConfigSafe).GetTag(u"MasterChef")
        except:
            oE.Log("Cannot create players list")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
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
                oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
                sys.exit()
        
    def Save(self):
        try:
            if self.Filename != "":
                config.SaveToFile(self.XML.GetRoot(), self.Filename)
        except:
            oE.Log(u"Cannot save players list")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            #sys.exit()
        
    #возвращает имя файла для заданного имени игрока
    def FilenameFor(self, name):
        return self.XML.Subtags(name).Get().GetStrAttr(u"file")
        
    #возвращает список игроков для диалогов
    def GetPlayerList(self):
        #return [Str_Players_Create]+[x.GetContent() for x in self.XML]
        return [x.GetContent() for x in self.XML]
        
    def CreatePlayer(self, name):
        try:
            filename = u"data/"+name+".def"
            tmp = scraft.Xdata("player(%s) { file = '%s' }" % (name, filename)).GetTag()
            tmp.SetContent(name)
            self.XML.InsertCopyOf(tmp)
            self.Save()
            globalvars.CurrentPlayer = Player()
            globalvars.CurrentPlayer.Read(name)
            globalvars.CurrentPlayer.Save()
        except:
            oE.Log("Cannot create player "+name)
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
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
            oE.Log("Cannot remove player "+name)
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
    #выбор игрока по номеру из списка
    def SelectPlayer(self, name):
        try:
            #name = self.GetPlayerList()[no]
            globalvars.GameConfig.SetStrAttr("Player", name)
            config.SaveGameConfig()
            globalvars.CurrentPlayer.Read(name)
        except:
            oE.Log("Cannot select player "+str(no))
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
