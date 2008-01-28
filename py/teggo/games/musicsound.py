#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback
from random import choice

import scraft
from scraft import engine as oE

TheMusician = None

#инициализация - вызвать перед первым обращением!
def Init(filename):
    global TheMusician
    try:
        TheMusician = Musician(filename)
    except:
        TheMusician = None
        oE.Log("Music/Sound initialization failed")
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))

def SetState(state):
    global TheMusician
    if TheMusician != None:
        TheMusician.SetState(state)
    else:
        oE.Log("MusicSound not initialized")
    
def Pause(flag):
    global TheMusician
    if TheMusician != None:
        TheMusician.SetPause(flag)
    else:
        oE.Log("MusicSound not initialized")
    
def PlaySound(sound, channel = None):
    global TheMusician
    if TheMusician != None:
        TheMusician.PlaySound(sound, channel)
    else:
        oE.Log("MusicSound not initialized")


#--------------------------------
# Управляет проигрыванием музыки
# Текущее состояние полностью опрелделяет фоновые треки
# На данный момент фоновый трек поддерживается один, и он играется в цикле
#--------------------------------

class Musician(scraft.Dispatcher):
    def __init__(self, filename):
        try:
            self.DefData = oE.ParseDEF(filename)
            self.State = None
            self.NextStates = []
            self.QueNo = oE.executor.Schedule(self)
        except:
            oE.Log("Cannot create Musician object")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
    def SetState(self, state):
        if state in [x.GetContent() for x in self.DefData.GetTag("MusicThemes").Tags("State")]:
            self.NextStates.append(state)
            
    def _PlayNewMelody(self):
        tmpNewMelody = choice(eval(self.DefData.GetTag("MusicThemes").GetSubtag(self.State).GetStrAttr("tracks")))
        oE.PlaySound(tmpNewMelody, self.DefData.GetIntAttr("Channel_Music"), self)
        
    def _OnStopSound(self, sound, channel, cookie, x):
        if not x:
            self._PlayNewMelody()
        
    def _OnExecute(self, que):
        if self.NextStates != []:
            if self.NextStates[-1] != self.State:
                self.State = self.NextStates[-1]
                oE.StopSound(self.DefData.GetIntAttr("Channel_Music"))
                self._PlayNewMelody()
            self.NextStates = []
        return scraft.CommandStateRepeat
        
    def SetPause(self, flag):
        oE.StopSound(self.DefData.GetIntAttr("Channel_Music"))
        oE.StopSound(self.DefData.GetIntAttr("Channel_Default"))
        if not flag:
            self._PlayNewMelody()
        
    def PlaySound(self, sound, channel = None):
        if channel == None:
            channel = self.DefData.GetIntAttr("Channel_Default")
        if sound != "":
            oE.PlaySound(sound, channel)
        else:
            oE.Log("No sound specified")

