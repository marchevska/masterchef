#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef 
Управление подсказками по игре
"""

import scraft
from scraft import engine as oE
import globalvars
from constants import *

class Advisor(scraft.Dispatcher):
    def __init__(self):
        self.QueNo = oE.executor.Schedule(self)
        
    def _OnExecute(self, que):
        while True:
            tmp = globalvars.BlackBoard.Inspect(BBTag_Hints)
            if tmp != None:
                if globalvars.HintsInfo.GetSubtag(tmp["event"]) != None:
                    print globalvars.HintsInfo.GetSubtag(tmp["event"])
                    if not globalvars.CurrentPlayer.GetLevelParams(tmp["event"]).GetBoolAttr("seen") \
                            and globalvars.GameConfig.GetBoolAttr("Hints"):
                        
                        #show!
                        globalvars.CurrentPlayer.SetLevelParams(tmp["event"], { "seen": True })
                        break
            else:
                break
        return scraft.CommandStateRepeat
        
    def Freeze(self, flag):
        if flag:
            oE.executor.GetQueue(self.QueNo).Suspend()
        else:
            oE.executor.GetQueue(self.QueNo).Resume()
        
    def Kill(self):
        oE.executor.DismissQueue(self.QueNo)
        
