#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
������ �� ������� ������� � � ��������� �������
"""

import os, os.path
import sys
import scraft
from scraft import engine as oE
from configconst import *
import config
import defs
import globalvars
import string, traceback

AllBoolAttrs = ("played", "unlocked", "expert", "seen", "beat1st", "beat2nd", "passed" )
AllIntAttrs = ("hiscore", "place")

class Player:

    #------------------------------------
    #������� ������ ������� ������
    #------------------------------------
    def __init__(self):
        self.Name = ""
        self.Level = None       #��������� �� ���� ������ � LevelProgress
        self.Filename = ""
        self.EpisodeResults = {}
        try:
            self.XML = oE.ParseDEF(globalvars.File_DummyProfile).GetTag(DEF_Header)
        except:
            oE.Log("Cannot create player profile")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
            
    #------------------------------------
    # ��������� ������� ������ �� �����
    #------------------------------------
    def Read(self, name=""):
        self.Name = name
        self.Level = None
        self.Filename = ""
        dummyXML = oE.ParseDEF(globalvars.File_DummyProfile).GetTag(DEF_Header)
        try:
            if name != "":
                filename = globalvars.PlayerList.FilenameFor(name)
                self.Filename = filename
                if config.FileValid(filename):
                    self.XML = oE.ParseDEF(filename).GetTag(DEF_Header)
                else:
                    self.XML = dummyXML
            else:
                self.XML = dummyXML
        except:
            try:
                self.XML = dummyXML
            except:
                #���� �����-����� �� ����� ���������
                oE.Log("Cannot read player info for "+name)
                oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
                sys.exit()
        #append nodes from dummy profile if necessary
        for tmpNode in dummyXML.Tags():
            tmp = self.XML.GetSubtag(tmpNode.GetContent(), tmpNode.GetName())
            if tmp == None:
                tmp = self.XML.Insert(tmpNode.GetName())
                tmp.SetContent(tmpNode.GetContent())
            for attr in AllBoolAttrs:
                if tmpNode.HasAttr(attr) and not tmp.HasAttr(attr):
                    tmp.SetBoolAttr(attr, tmpNode.GetBoolAttr(attr))
            for attr in AllIntAttrs:
                if tmpNode.HasAttr(attr) and not tmp.HasAttr(attr):
                    tmp.SetIntAttr(attr, tmpNode.GetIntAttr(attr))
        self.Save()
        
    #------------------------------------
    # ��������� ������� ������ � ����
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
    # �������� ���������� ��������� ������
    #------------------------------------
    def LastUnlockedLevel(self, type = "level"):
        tmp = filter(lambda x: x.GetBoolAttr("unlocked"), self.XML.Tags(type))
        if len (tmp)>0:
            return tmp[-1].GetContent()
        else:
            return ""
        
    def NewUnlockedLevel(self, type = "level"):
        if self.XML.HasAttr("newUnlocked") and self.XML.GetStrAttr("newUnlocked")!="":
            return self.XML.GetStrAttr("newUnlocked")
        return ""
        
    def PopNewUnlockedLevel(self):
        self.XML.SetStrAttr("newUnlocked", "")
        
    def _UnlockEntry(self, entry):
        if not entry.GetBoolAttr("unlocked") and entry.GetName() in ("comic", "intro", "outro", "level"):
            self.XML.SetStrAttr("newUnlocked", entry.GetContent())
        entry.SetBoolAttr("unlocked", True)
        
    #------------------------------------
    # ���������� ������� �������
    #------------------------------------
    def SetLevel(self, level):
        try:
            self.Level = level#.Clone()
            tmpNode = self.XML.GetSubtag(level.GetContent())
            if level.GetName() in ("comic", "intro"):
                #���� ������ ��� �����: �������� � ������� ������ ������� ��� ���������
                tmpNode.SetBoolAttr("seen", True)
                #���� ������� - ������, �� �������� ��������� ������� ��� ������ ��� �����������
                if level.Next():
                    tmpNextLevel = self.XML.GetSubtag(level.Next().GetContent())
                    if tmpNextLevel.HasAttr("unlocked"):
                        self._UnlockEntry(tmpNextLevel)
                        #tmpNextLevel.SetBoolAttr("unlocked", True)
                #��������� ������ ����� �����, ���� ����������
                if level.GetName() == "intro":
                    self._UnlockEntry(self.XML.GetSubtag(level.GetStrAttr("episode")))
                    #self.XML.GetSubtag(level.GetStrAttr("episode")).SetBoolAttr(u"unlocked", True)
            
            elif level.GetName() == "outro":
                #���� �����: �������� � ������� ������ ������� ��� ���������
                tmpNode.SetBoolAttr("seen", True)
                self._ReviewEpisodeResults(level)
                #��������� ������� ��� ������������ ���������� ������
                if level.Next() and self.EpisodeResults[level.GetStrAttr("episode")]["pass"]:
                    tmpNextLevel = self.XML.GetSubtag(level.Next().GetContent())
                    if tmpNextLevel.HasAttr("unlocked"):
                        self._UnlockEntry(tmpNextLevel)
            
            elif level.GetName() == "level":
                #���� �������: �������� � ������� ������ ������� ��� �������
                tmpNode.SetBoolAttr(u"played", True)
            self.Save()
        except:
            oE.Log("Cannot set level to "+level.GetContent())
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
    #------------------------------------
    # ���������� ���������� ��� ��������� �������
    # level - ��� outro-���� � levelprogress
    # ��� ������� ���������� ��� ��������� outro-�������
    # � ��� ���������� ������
    #------------------------------------
    def _ReviewEpisodeResults(self, level):
        try:
            #outro-���� � episode-���� � ������� ������
            tmpEpisodeName = level.GetStrAttr("episode")
            tmpOutroNode = self.XML.GetSubtag(level.GetContent())
            tmpOldOutroNode = tmpOutroNode.Clone()
            tmpEpisodeNode = self.XML.GetSubtag(tmpEpisodeName)
            
            #����� ����� �� ������ - ������������ �����������
            tmpSum = reduce(lambda x,y: x+y,
                        map(lambda x: (x.GetBoolAttr("expert"))*globalvars.GameSettings.GetIntAttr("expertPoints")+\
                        (x.GetIntAttr("hiscore")>0 and not x.GetBoolAttr("expert"))*globalvars.GameSettings.GetIntAttr("levelPoints"),
                        map(lambda y: self.XML.GetSubtag(y), eval(level.GetStrAttr("sum")))))
            tmpEpisodeNode.SetIntAttr("points", tmpSum)
            
            #��������� - ������� �� ������ �� ��������
            tmpPass = True
            #��������� ����� � ������ �� ��������
            tmpConditionsPlace = eval(level.GetStrAttr("passIf"))
            for episode in tmpConditionsPlace.keys():
                tmpResults = dict(map(lambda x: (x[0], x[1]['score']),
                    eval(globalvars.LevelProgress.GetTag("People").GetSubtag(episode).GetStrAttr("people")).items()))
                tmpResults[globalvars.GameSettings.GetStrAttr("charName")] = self.XML.GetSubtag(episode).GetIntAttr("points")
                tmp = tmpResults.items()
                #���������� �� �������� ���������� �����
                tmp.sort(lambda x,y: cmp(y[1], x[1]))
                tmpPlace = tmp.index((globalvars.GameSettings.GetStrAttr("charName"), self.XML.GetSubtag(episode).GetIntAttr("points")))+1
                #���� ����� �� ���������� �����, ��� � �������� ��������� ����� - �������� �����!
                if tmpPlace < len(tmp):
                    if tmp[tmpPlace][1] == self.XML.GetSubtag(episode).GetIntAttr("points"):
                        tmpEntry = tuple(tmp[tmpPlace])
                        tmp[tmpPlace] = tmp[tmpPlace-1]
                        tmp[tmpPlace-1] = tmpEntry
                        tmpPlace = tmpPlace + 1
                if tmpPlace > tmpConditionsPlace[episode]:
                    tmpPass = False
            #��������� ���� � ������ �� �������� � ��������� ����
            if level.HasAttr("passScore"):
                tmpConditionsScore = eval(level.GetStrAttr("passScore"))
                for episode in tmpConditionsScore.keys():
                    if self.XML.GetSubtag(episode).GetIntAttr("points") < tmpConditionsScore[episode]:
                        tmpPass = False
            if level.HasAttr("sumScore"):
                tmpPlayerSumScore = reduce(lambda x,y: x+y, map(lambda x: self.XML.GetSubtag(x).GetIntAttr("points"),
                            eval(globalvars.GameSettings.GetStrAttr("settings"))))
                if tmpPlayerSumScore < level.GetIntAttr("sumScore"):
                    tmpPass = False
                    
            #���������� ���������� � �������
            self.EpisodeResults[tmpEpisodeName] = { "scores": tmp, "place": tmpPlace, "pass": tmpPass }
            if tmpPass:
                if tmpPlace <= 1 and tmpPass:
                    tmpOutroNode.SetBoolAttr("beat1st", True)
                if tmpPlace <= 2 and tmpPass:
                    tmpOutroNode.SetBoolAttr("beat2nd", True)
                if tmpPass:
                    tmpOutroNode.SetBoolAttr("passed", True)
                if tmpPass:
                    tmpOutroNode.SetIntAttr("place", tmpPlace)
                    
            #���������� ���������� ���������� � ��� ����������
            if ((tmpOutroNode.GetBoolAttr("beat1st") != tmpOldOutroNode.GetBoolAttr("beat1st")) or \
                    (tmpOutroNode.GetBoolAttr("beat2nd") != tmpOldOutroNode.GetBoolAttr("beat2nd")) or \
                    (tmpOutroNode.GetBoolAttr("passed") != tmpOldOutroNode.GetBoolAttr("passed")) or \
                    not (tmpOutroNode.GetBoolAttr("seen"))) and \
                    tmpOutroNode.GetBoolAttr("unlocked"):
                self.XML.SetStrAttr("newUnlocked", level.GetContent())
        except:
            oE.Log("Cannot update player profile")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
    #------------------------------------
    #��������� ������� ��� ������������ ���������� ������ ����� outro
    #------------------------------------
    def GetScoresPlaceAndCondition(self):
        return self.EpisodeResults[self.Level.GetStrAttr("episode")]
        
    def GetLevel(self):
        return self.Level
        
    def NextLevel(self):
        self.Level = self.Level.Next()
        
    #------------------------------------
    # ���������� ���� �������� ������ �� ������� ������ �� �� �����
    # (�� ���� ���������� �������� ������, ��� �������, ��� ���������...)
    #------------------------------------
    def GetLevelParams(self, level):
        if self.XML.GetSubtag(level) != None:
            return self.XML.GetSubtag(level)
        else:
            return oE.ParseDEF(globalvars.File_DummyProfile).GetTag(DEF_Header).GetSubtag(level)
        
    #------------------------------------
    # �������� ��������� ������ � ������� ������
    #------------------------------------
    def SetLevelParams(self, level, params):
        try:
            tmp = self.XML.GetSubtag(level)
            for attr in AllBoolAttrs:
                if params.has_key(attr):
                    tmp.SetBoolAttr(attr, params[attr])
            for attr in AllIntAttrs:
                if params.has_key(attr):
                    tmp.SetIntAttr(attr, params[attr])
            self.Save()
        except:
            oE.Log("Cannot update player profile")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
    #------------------------------------
    # �������� ���������� �������� ������ + � ������� ����
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
                    #���������, ���������� �� ���� ������; 
                    #���� �� - ��������� ��������� � ��������� �������
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
                
            #��������� � �������� ��������� ���������� �� ���� �������
            #�� ������� ����������� ������ - 5 �����, �� ���������� - 10
            for tmp in globalvars.LevelProgress.GetTag("Levels").Tags("outro"):
                self._ReviewEpisodeResults(tmp)
                #tmpSum = reduce(lambda x,y: x+y,
                #    map(lambda x: self.XML.GetSubtag(x).GetIntAttr("hiscore"), eval(tmp.GetStrAttr("sum"))))
                #tmpSum = reduce(lambda x,y: x+y,
                #        map(lambda x: (x.GetBoolAttr("expert"))*globalvars.GameSettings.GetIntAttr("expertPoints")+\
                #        (x.GetIntAttr("hiscore")>0 and not x.GetBoolAttr("expert"))*globalvars.GameSettings.GetIntAttr("levelPoints"),
                #        map(lambda y: self.XML.GetSubtag(y), eval(tmp.GetStrAttr("sum")))))
                #if tmpSum == globalvars.GameSettings.GetIntAttr("expertAll") and \
                #        self.XML.GetSubtag(tmp.GetStrAttr("episode")).GetIntAttr("points") < tmpSum:
                #    self.XML.SetStrAttr("newUnlocked", tmp.GetContent())
                #self.XML.GetSubtag(tmp.GetStrAttr("episode")).SetIntAttr("points", tmpSum)
            self.Save()
        except:
            oE.Log("Cannot update player profile")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
    #------------------------------------
    # ���������� ������ ����� ��������, �� ���
    #�� ���������� �������� � ������� ��������
    #------------------------------------
    def JustUnlockedRecipes(self, setting):
        tmpRecipes = filter(lambda x: globalvars.RecipeInfo.GetSubtag(x).GetStrAttr("setting") == setting,
                                map(lambda x: x.GetContent(), globalvars.RecipeInfo.Tags()))
        return filter(lambda x: self.GetLevelParams(x).GetBoolAttr("unlocked") == True and
                    self.GetLevelParams(x).GetBoolAttr("seen") == False,
                    tmpRecipes)
            
#------------------------------------
# ���������� ������� �������
#------------------------------------
class PlayerList:
    def __init__(self):
        try:
            self.Filename = ""
            self.XML = oE.ParseDEF(globalvars.File_PlayersConfigSafe).GetTag(DEF_Header)
        except:
            oE.Log("Cannot create players list")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
    #��������� � ������ ������ ������� (� ������ ����)
    def Read(self):
        try:
            self.Filename = globalvars.File_PlayersConfig
            if config.FileValid(self.Filename):
                self.XML = oE.ParseDEF(self.Filename).GetTag(DEF_Header)
            globalvars.CurrentPlayer = Player()
            globalvars.CurrentPlayer.Read(globalvars.GameConfig.GetStrAttr("Player"))
        except:
            try:
                self.XML = oE.ParseDEF(globalvars.File_PlayersConfigSafe).GetTag(DEF_Header)
            except:
                #���� �����-����� �� ����� ���������
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
        
    #���������� ��� ����� ��� ��������� ����� ������
    def FilenameFor(self, name):
        return self.XML.Subtags(name).Get().GetStrAttr(u"file")
        
    #���������� ������ ������� ��� ��������
    def GetPlayerList(self):
        return [x.GetContent() for x in self.XML]
        
    def CreatePlayer(self, name):
        try:
            filename = globalvars.DataDirectory+name+".def"
            #filename = "data/"+name+".def"
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
        
    # �������� ������ �� �����
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
        
    #����� ������ �� ������ �� ������
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
        
