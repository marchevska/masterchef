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
from guielements import MakeSprite, MakeDummySprite
from extra import *
import traceback, string

#---------------------
# конвейер
# задние предметы толкают передние
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
        return 1.0*(self.X0)
        
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
            self.Tokens[i].MoveTo(self.FnX(self.FnP(self.TokensCrd[i])), self.FnY(self.FnP(self.TokensCrd[i])))
        
        return scraft.CommandStateRepeat
        
        
    def _PutNewToken(self):
        self.Tokens.append(Token(self, RandomKeyByRates(dict(map(lambda x: (x.GetStrAttr("type"), x.GetIntAttr("rate")),
                       globalvars.LevelSettings.GetTag("IngredientRates").Tags("Ingredient"))))))
        if len(self.TokensCrd) == 0:
            self.TokensCrd.append(0)
        else:
            self.TokensCrd.append(self.TokensCrd[-1] - self.DS)
        
    def _PutTokenAt(self, type, position):
        tmpPrevTokens = self.Tokens[0:position]
        tmpPrevCrd = self.TokensCrd[0:position]
        if position < len(self.Tokens):
            tmpNextTokens = self.Tokens[position:len(self.Tokens)]
            tmpNextCrd = self.TokensCrd[position:len(self.Tokens)]
        else:
            tmpNextTokens = []
            tmpNextCrd = []
        if len(self.Tokens) == 0:
            tmpNewCrd = 0
        elif position == len(self.Tokens):
            tmpNewCrd = self.TokensCrd[position-1] - self.DS
        else:
            tmpNewCrd = self.TokensCrd[position] + self.DS
            
        self.Tokens = tmpPrevTokens + [Token(self, type)] + tmpNextTokens
        self.TokensCrd = tmpPrevCrd + [tmpNewCrd] + tmpNextCrd
        
    def SendCommand(self, cmd, param = None):
        if cmd == Cmd_PickToken:
            idx = self.Tokens.index(param)
            self.RemoveToken(param)
            globalvars.Board.SendCommand(Cmd_PickFromConveyor,
                                         { "where": self, "type": param.type, "position": idx })
        elif cmd == Cmd_ReturnToConveyor:
            self._PutTokenAt(param["type"], param["position"])
        
    def RemoveToken(self, token):
        idx = self.Tokens.index(token)
        self.Tokens.pop(idx)
        self.TokensCrd.pop(idx)
        token.Kill()
        
    def DropTokens(self):
        pass
        
    def RemoveTokens(self):
        pass
        
    def Freeze(self, flag):
        if flag:
            oE.executor.GetQueue(self.QueNo).Suspend()
        else:
            oE.executor.GetQueue(self.QueNo).Resume()
            
    def Clear(self):
        oE.executor.DismissQueue(self.QueNo)
        for tmp in self.Tokens:
            tmp.Kill()
        self.Tokens = []
        self.TokenCrd = []

#---------------------
# класс токена
#---------------------

class Token(scraft.Dispatcher):
    def __init__(self, whose, type):
        self.type = type
        self.sprite = MakeSprite(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(type).GetStrAttr("src"), Layer_Tokens,
                                 { "hotspot": scraft.HotspotCenter, "dispatcher": self })
        self.whose = whose
        
    def MoveTo(self, newX, newY):
        self.sprite.x, self.sprite.y = newX, newY
        
    def _OnMouseClick(self, sprite, x, y, button):
        if button == 1:
            self.whose.SendCommand(Cmd_PickToken, self)
            globalvars.LastCookie = Cmd_None
        
    def Kill(self):
        self.sprite.Dispose()
        

