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
from configconst import *
import gamegui

#------------
# Советник
# Показывает подсказки в соответствии с ивентами
# Этот же механизм реализует туториал
#------------

class Advisor(scraft.Dispatcher):
    def __init__(self):
        self.QueNo = oE.executor.Schedule(self)
        
    def _OnExecute(self, que):
        while True:
            #читаем очередь ивентов,
            #пока не найдем ивент, порождающий подсказку
            tmp = globalvars.BlackBoard.Inspect(BBTag_Hints)
            if tmp != None and globalvars.RunMode == RunMode_Play:
                tmpHintNode = globalvars.HintsInfo.GetSubtag(tmp["event"])
                if tmpHintNode != None:
                    #проверяем: можно ли показать данную подсказку:
                    #она не была показана ранее или многоразовая и подсказки разрешены
                    if (tmpHintNode.GetBoolAttr("showOnce") and \
                            tmpHintNode.GetIntAttr("minLevel") <= globalvars.CurrentPlayer.GetLevel().GetIntAttr("no") <= tmpHintNode.GetIntAttr("maxLevel") and \
                            not globalvars.CurrentPlayer.GetLevelParams(tmp["event"]).GetBoolAttr("seen") \
                            and globalvars.CurrentPlayer.XML.GetBoolAttr("Hints")):
                        globalvars.CurrentPlayer.SetLevelParams(tmp["event"], { "seen": True })
                        gamegui.ShowHint(tmp["event"], tmp["where"])
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
        
