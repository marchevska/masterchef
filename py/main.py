#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef 
Основной модуль
"""

import os.path
import pyteggo2
import os, sys, traceback, string
import profile
import scraft
from scraft import engine as oE
from configconst import *
from gui import Gui
from gameboard import GameBoard
from playerlist import Player, PlayerList
from blackboard import BlackBoard
from extra import Timer, Cursor
import config
import globalvars
import defs

import gamegui
from teggo.games import musicsound

def Loading():
    #проверить - упакованы ресурсы или нет
    try:
        import _jungle
        if _jungle.compiled:
            pyteggo2.InitRoEfs(0)
            pyteggo2.MountRoEfs("*.dat","b470c392669c5d767b552d30af0a5bab")
    except:
        pass
    
    oE.logging = True
    oE.Init(scraft.DevDisableDrvInfo)
    oE.vMode = Video_Mode
    oE.background.color = 0x402020
    oE.rscpath = sys.argv[0][0:sys.argv[0].rfind("\\")+1]
    oE.SST = oE.rscpath + File_SST
    oE.title = Window_Title
    oE.nativeCursor = False
    oE.showFps = False
    
    config.GetFileLocations()
    defs.ReadLevelProgress()
    defs.ReadCuisine()
    defs.ReadResourceInfo()
    defs.ReadGameSettings()
    
    # определяем режим запуска - тест или реальная игра
    if len(sys.argv) >= 3 and globalvars.GameSettings.GetBoolAttr("debugMode"):
        if sys.argv[1] == "run" and globalvars.LevelProgress.GetTag("Levels").GetSubtag(sys.argv[2]) != None:
            globalvars.RunMode = RunMode_Test
        else:
            globalvars.RunMode = RunMode_Play
    else:
        globalvars.RunMode = RunMode_Play
    # конец кода определения типа запуска
    
    config.ReadGameConfig()
    config.ApplyOptions()
    config.ReadHiscores()
    config.ReadBestResults()
    
    globalvars.PlayerList = PlayerList()
    globalvars.PlayerList.Read()
    
    globalvars.BlackBoard = BlackBoard()
    
    musicsound.Init("def/sound.def")
    gamegui.InitGUI()
    
    globalvars.Board = GameBoard()
    globalvars.PausedState = False
    globalvars.ExitFlag = False
        
def MainLoop():
    if globalvars.RunMode == RunMode_Play:
        gamegui.ShowLogoSequence()
    
    # начало кода запуска заданного уровня
    if globalvars.RunMode == RunMode_Test:
        try:
            globalvars.GameConfig.SetBoolAttr("Fullscreen", False)
            config.ApplyOptions()
            globalvars.CurrentPlayer.Level = globalvars.LevelProgress.GetTag("Levels").GetSubtag(sys.argv[2])
            gamegui.PlayLevel()
        except:
            sys.exit()
    # конец кода запуска заданного уровня
    
    while not globalvars.ExitFlag:
        oE.NextEvent()
        if oE.EvtIsQuit():
            gamegui.AskForQuitGame()
        if oE.windowIsActive == globalvars.PausedState:
            globalvars.PausedState = not globalvars.PausedState
            gamegui.SetPause(globalvars.PausedState)
        if oE.EvtIsKeyDown():
            if oE.EvtKey() == scraft.Key_F4 and not oE.IsKeyPressed(scraft.Key_ALT):
                globalvars.GameConfig.SetBoolAttr("Fullscreen", not(globalvars.GameConfig.GetBoolAttr("Fullscreen")))
                config.ApplyOptions()
        oE.DisplayEx(60)
    

def ExitGame():    
    if globalvars.RunMode == RunMode_Play:
        config.SaveGameConfig()
        config.SaveBestResults()
        config.SaveHiscores()
        globalvars.PlayerList.Save()
        globalvars.CurrentPlayer.Save()
    
#profile.run('Loading()')
#profile.run('MainLoop()')
#profile.run('ExitGame()')
try:
    Loading()
    MainLoop()
    ExitGame()
except:
    print string.join(apply(traceback.format_exception, sys.exc_info()))

