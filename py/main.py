#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef 
�������� ������
"""

import sys
import scraft
from scraft import engine as oE
from configconst import *
from gui import Gui
from gameboard import GameBoard
from extra import *
import config
import playerlist
import globalvars
import defs

oE.logging = True
oE.Init(scraft.DevDisableDrvInfo)
oE.vMode = Video_Mode
oE.background.color = 0x402020
oE.rscpath = unicode(sys.argv[0][0:sys.argv[0].rfind("\\")+1])
oE.SST = File_SST
oE.title = Window_Title
oE.nativeCursor = False
oE.showFps = False

globalvars.RunMode = RunMode_Play
config.ReadGameConfig()
config.ApplyOptions()
config.ReadHiscores()
config.ReadBestResults()
playerlist.ReadPlayers()

defs.ReadLevelProgress()
defs.ReadCuisine()
defs.ReadResourceInfo()

globalvars.Cursor = Cursor()
globalvars.Timer = Timer()
globalvars.Musician = Musician()
globalvars.StateStack = []

globalvars.GUI = Gui()
globalvars.Board = GameBoard()
    
globalvars.ActiveGameSession = False

# ������ ���� ������� ��������� ������
if len(sys.argv) >= 3:
    if sys.argv[1] == "run":# and sys.argv[2] in globalvars.LevelProgress.keys():
        try:
            globalvars.RunMode = RunMode_Test
            globalvars.CurrentPlayer["Level"] = sys.argv[2]
            globalvars.GUI.JustRun()
        except:
            sys.exit()
    else:
        globalvars.RunMode = RunMode_Play
# ����� ���� ������� ��������� ������

while globalvars.StateStack[-1] != PState_EndGame:
    oE.NextEvent()
    #if oE.EvtIsESC() or oE.EvtIsQuit() :
    #    break
        #if globalvars.StateStack[-1] == PState_Edit:    
        #    globalvars.StateStack[-1] = PState_EndGame
    if oE.EvtIsKeyDown() :
        if oE.EvtKey() == scraft.Key_F3:
            globalvars.Board.Restart()
    if oE.EvtIsKeyDown() :
        if oE.EvtKey() == scraft.Key_F4 :
            globalvars.GameConfig["Fullscreen"] = not(globalvars.GameConfig["Fullscreen"])
            config.ApplyOptions()
    oE.DisplayEx(30) # 30 FPS

config.SaveGameConfig()
config.SaveHiscores()
playerlist.SavePlayers()
