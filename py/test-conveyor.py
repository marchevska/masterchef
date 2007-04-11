#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Тест механики с конвейером
"""

import scraft
from scraft import engine as oE
import globalvars
import defs
from constants import *
from configconst import *
from guielements import MakeSimpleSprite, MakeDummySprite, PushButton
from extra import *
import traceback, string
from random import choice

TokenRates = { "tomato": 5, "flour": 5, "avocado": 5,
              "banana": 5, "sugar": 5, "salmon": 5,
              "rice": 0 }

#---------------------
# класс конвейера
#---------------------

class Conveyor(scraft.Dispatcher):
    def __init__(self, x, y, v, ds):
        self.X0 = x
        self.Y0 = y
        self.V0 = v
        self.DS = ds
        self.Tokens = []
        self.TokensCrd = []
        self.QueNo = oE.executor.Schedule(self)
        
        
    def FnX(self, p):
        return 1.0*(self.X0 + 10*p)
        
    def FnY(self, p):
        return 1.0*(self.Y0 + 10*p)
        
    def FnS(self, p):
        return 1
        
    def FnP(self, s):
        return 1.0*s/14.1
        
    def _OnExecute(self, que):
        if len(self.Tokens) == 0:
            self._PutNewToken()
        elif self.TokensCrd[-1] >= self.DS:
            self._PutNewToken()
            
        for i in range(len(self.Tokens)):
            if i<len(self.Tokens) - 1:
                if self.TokensCrd[i] <= self.TokensCrd[i+1] + self.DS:
                    self.TokensCrd[i] += self.V0*que.delta*0.001
            else:
                self.TokensCrd[i] += self.V0*que.delta*0.001
            #self.TokensCrd[i] = self.V0*que.millis*0.001 - self.DS*i
            self.Tokens[i].x = self.FnX(self.FnP(self.TokensCrd[i]))
            self.Tokens[i].y = self.FnY(self.FnP(self.TokensCrd[i]))
        
        return scraft.CommandStateRepeat
        
        
    def _PutNewToken(self):
        self.Tokens.append(MakeSimpleSprite("ingredient.mushroom", Layer_Tokens))
        if len(self.TokensCrd) == 0:
            self.TokensCrd.append(0)
        else:
            self.TokensCrd.append(self.TokensCrd[-1] - self.DS)
        
    def RemoveRandomToken(self):
        i = choice(range(len(self.Tokens)))
        self.Tokens[i].Dispose()
        self.Tokens.pop(i)
        self.TokensCrd.pop(i)
        
    
oE.logging = True
oE.Init(scraft.DevDisableDrvInfo)
oE.vMode = Video_Mode
oE.background.color = 0x402020
oE.rscpath = unicode(sys.argv[0][0:sys.argv[0].rfind("\\")+1])
oE.SST = File_SST
oE.title = "Conveyor Test"
oE.nativeCursor = False
oE.showFps = True
oE.fullscreen = False

defs.ReadCuisine()
defs.ReadResourceInfo()

globalvars.Cursor = Cursor()

Conveyor = Conveyor(100, 100, 25, 50)

while True:
    oE.NextEvent()
    if oE.EvtIsESC() or oE.EvtIsQuit() :
        break
    if oE.EvtIsKeyDown() :
        if oE.EvtKey() == scraft.Key_F3:
            Conveyor.RemoveRandomToken()
    oE.DisplayEx(55) # 30 FPS

