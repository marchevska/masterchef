#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Управление профилями и списком игроков
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
    #������� ������ ������� ������
    #------------------------------------
    def __init__(self):
        self.Name = ""
        self.Level = None       #��������� �� ���� ������ � LevelProgress
        self.Filename = ""
        try:
            self.XML = oE.ParseDEF(File_DummyProfile).GetTag(u"MasterChef")
        except:
            oE.Log(unicode("Cannot create player profile"))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
            
    #------------------------------------
    # ��������� ������� ������ �� �����
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
                #���� �����-����� �� ����� ���������
                oE.Log(unicode("Cannot read player info for "+name))
                oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
                sys.exit()
            
    #------------------------------------
    # ��������� ������� ������ � ����
    #------------------------------------
    def Save(self):
        try:
            if self.Filename != "":
                tmpDir = os.path.dirname(self.Filename)
                if not os.access(tmpDir, os.W_OK):
                    os.mkdir(tmpDir)
                self.XML.GetRoot().StoreTo(self.Filename)
        except:
            oE.Log(unicode("Cannot save player info for "+self.Name))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    #------------------------------------
    # ��������� �� ��������� �������� ������� ��� ������ - �� �� �������� type
    #------------------------------------
    def LastUnlockedLevel(self, type = u"level"):
        tmp = filter(lambda x: x.GetBoolAttr(u"unlocked"), self.XML.Tags(type))
        if len (tmp)>0:
            return tmp[-1]
        else:
            return None
        
    #------------------------------------
    # ���������� ������� �������
    #------------------------------------
    def SetLevel(self, level):
        try:
            self.Level = level.Clone()
            if level.GetName() == u"comic":
                #���� ������: �������� � ������� ������ ������ ��� ���������
                tmpNode = defs.GetTagWithContent(self.XML, u"comic", level.GetContent())
                tmpNode.SetBoolAttr(u"seen", True)
                #���� ������� - ������, �� �������� ��������� ������� ��� ������ ��� �����������
                tmpNextLevel = defs.GetTagWithContent(self.XML, level.Next().GetName(), level.Next().GetContent())
                if tmpNextLevel.HasAttr(u"unlocked"):
                    tmpNextLevel.SetBoolAttr(u"unlocked", True)
            elif level.GetName() == u"level":
                #���� �������: �������� � ������� ������ ������� ��� �������
                tmpNode = defs.GetTagWithContent(self.XML, u"level", level.GetContent())
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
    #���������� ���� ������ �� ��� �����
    #------------------------------------
    def GetLevelParams(self, level):
        return self.XML.GetSubtag(level)
        
    def SetLevelParams(self, level, params):
        pass
        
        
class PlayerList:
    def __init__(self):
        try:
            self.Filename = ""
            self.XML = oE.ParseDEF(File_PlayersConfigSafe).GetTag(u"MasterChef")
        except:
            oE.Log(unicode("Cannot create players list"))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
    #��������� � ������ ������ ������� (� ������ ����)
    def Read(self):
        try:
            #if config.FileValid(File_PlayersConfig):
            #    PlayersIterator = oE.ParseDEF(File_PlayersConfig).GetTag(u"MasterChef").IterateTag(u"player")
                #while PlayersIterator.Next():
                #    tmpPl = PlayersIterator.Get()
                #    self.Players[tmpPl.GetContent()] = tmpPl.GetStrAttr(u"file")
            self.Filename = File_PlayersConfig
            if config.FileValid(File_PlayersConfig):
                self.XML = oE.ParseDEF(File_PlayersConfig).GetTag(u"MasterChef")
            globalvars.CurrentPlayer = Player()
            globalvars.CurrentPlayer.Read(globalvars.GameConfig["Player"])
        except:
            try:
                self.XML = oE.ParseDEF(File_PlayersConfigSafe).GetTag(u"MasterChef")
            except:
                #���� �����-����� �� ����� ���������
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
        
    #���������� ��� ���� ��� ��������� ����� ������
    def FilenameFor(self, name):
        return self.XML.Subtags(unicode(name)).Get().GetStrAttr(u"file")
        
    #���������� ������ ������� ��� ��������
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
            sys.exit()
        
    #����� ������ �� ������ �� ������
    def SelectPlayer(self, name):
        try:
            #name = self.GetPlayerList()[no]
            globalvars.GameConfig["Player"] = name
            config.SaveGameConfig()
            globalvars.CurrentPlayer.Read(name)
        except:
            oE.Log(unicode("Cannot select player "+str(no)))
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            sys.exit()
        
