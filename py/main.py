#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef 
Основной модуль
"""

import os, sys
import scraft
from scraft import engine as oE
from configconst import *
from gui import Gui
from gameboard import GameBoard
from playerlist import Player, PlayerList
from blackboard import BlackBoard
from extra import *
import config
import globalvars
import defs

oE.logging = False
oE.Init(scraft.DevDisableDrvInfo)
oE.vMode = Video_Mode
oE.background.color = 0x402020
oE.rscpath = sys.argv[0][0:sys.argv[0].rfind("\\")+1]
oE.SST = File_SST
oE.title = Window_Title
oE.nativeCursor = False
oE.showFps = False

defs.ReadLevelProgress()
defs.ReadCuisine()
defs.ReadResourceInfo()
defs.ReadGameSettings()

# определяем режим запска - тест или реальная игра
if len(sys.argv) >= 3:
    if sys.argv[1] == "run" and globalvars.LevelProgress.GetTag("Levels").GetSubtag(sys.argv[2]) != None:
        globalvars.RunMode = RunMode_Test
    else:
        globalvars.RunMode = RunMode_Play
else:
    globalvars.RunMode = RunMode_Play
# конец кода определения типа запуска

config.GetFileLocations()
config.ReadGameConfig()
config.ApplyOptions()
#config.ReadHiscores()
config.ReadBestResults()

globalvars.PlayerList = PlayerList()
globalvars.PlayerList.Read()

globalvars.BlackBoard = BlackBoard()
globalvars.Cursor = Cursor()
globalvars.Timer = Timer()
globalvars.Musician = Musician()
globalvars.StateStack = []

globalvars.GUI = Gui()
globalvars.Board = GameBoard()
globalvars.PausedState = False
    
# начало кода запуска заданного уровня
if globalvars.RunMode == RunMode_Test:
    try:
        globalvars.CurrentPlayer.Level = globalvars.LevelProgress.GetTag("Levels").GetSubtag(sys.argv[2])
        globalvars.GUI.JustRun()
    except:
        sys.exit()
# конец кода запуска заданного уровня

while globalvars.StateStack[-1] != PState_EndGame:
    oE.NextEvent()
    #if oE.EvtIsESC() or oE.EvtIsQuit() :
    #    break
    if oE.windowIsActive == globalvars.PausedState:
        globalvars.PausedState = not globalvars.PausedState
        globalvars.GUI.SetPauseState(globalvars.PausedState)
    if oE.EvtIsKeyDown():
        if oE.EvtKey() == scraft.Key_F4 and not oE.IsKeyPressed(scraft.Key_ALT):
            globalvars.GameConfig.SetBoolAttr("Fullscreen", not(globalvars.GameConfig.GetBoolAttr("Fullscreen")))
            config.ApplyOptions()
    oE.DisplayEx(30)

if globalvars.RunMode == RunMode_Play:
    config.SaveGameConfig()
    config.SaveBestResults()
    #config.SaveHiscores()
    globalvars.PlayerList.Save()
    globalvars.CurrentPlayer.Save()

