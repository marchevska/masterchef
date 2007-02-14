#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef 
Customer class
"""

import string, traceback, sys
import scraft
from scraft import engine as oE
import globalvars
from constants import *
from guielements import MakeSimpleSprite
from extra import Animator
from random import randint

#------------
# ����������; ����� ����������, ���������� � ���������
# ���������� ���������� � �������� �������
# � ���������� ��� ������������ ��� � ������� ���������
# ���� ���������� ������ �������� (0 ��������), ���������� ������
#------------
class Customer(scraft.Dispatcher):
    def __init__(self, type, host):
        self.Type = type
        self.Host = host
        self.Sprite = MakeSimpleSprite(globalvars.CustomersInfo[type]["src"], Layer_Customer,
                        host.CrdX + Crd_CustomerDx, host.CrdY + Crd_CustomerDy, scraft.HotspotCenterBottom)
        self.Animator = CustomersAnimator(self.Sprite,
                globalvars.CustomerAnimations[globalvars.CustomersInfo[type]["animation"]])
        self.HeartSprites = []
        for i in range(Const_MaxHearts):
            self.HeartSprites.append(MakeSimpleSprite(u"heart", Layer_Recipe,
                        host.CrdX + Crd_HeartsDx + i*Crd_HeartSpritesDx, host.CrdY + Crd_HeartsDy + i*Crd_HeartSpritesDy))
        self._SetHearts(globalvars.CustomersInfo[type]["heartsOnStart"])
        self._SetState(CustomerState_Ordering)
        self.QueNo = oE.executor.Schedule(self)
        
    def GiveSweet(self):
        self.AddHearts(1)
        self._SetState(CustomerState_GotGift)
        
    def GiveGift(self):
        self.AddHearts(3)
        self._SetState(CustomerState_GotGift)
        
    def AddHearts(self, no):
        self._SetHearts(self.Hearts + no)
        
    def _SetHearts(self, no):
        no = max(0, min(no, Const_MaxHearts))
        if no>0:
            self.Hearts = no
            for i in range(no):
                self.HeartSprites[i].visible = True
            for i in range(no, Const_MaxHearts):
                self.HeartSprites[i].visible = False
            self.Animator.SetState(str(self.Hearts)+"Hearts")
        else:
            self._SetState(CustomerState_GoAway)
        
    def _SetState(self, state):
        self.State = state
        if state == CustomerState_Ordering:
            self.Animator.SetState("Order")
            self.NextStateTime = randint(globalvars.CustomersInfo[self.Type]["orderingTimeMin"]*1000,
                                         globalvars.CustomersInfo[self.Type]["orderingTimeMax"]*1000)
            
        elif state == CustomerState_Wait:
            self.NextStateTime = randint(globalvars.CustomersInfo[self.Type]["patientTimeMin"]*1000,
                                         globalvars.CustomersInfo[self.Type]["patientTimeMax"]*1000)
            self._SetHearts(self.Hearts)
            
        elif state == CustomerState_GotGift:
            self.Animator.SetState("GotGift")
            self.NextStateTime = randint(globalvars.CustomersInfo[self.Type]["gotGiftTimeMin"]*1000,
                                         globalvars.CustomersInfo[self.Type]["gotGiftTimeMin"]*1000)
            
        elif state == CustomerState_GoAway:
            self.Host.SendCommand(Cmd_FlopOrder)
            self.Animator.SetState("GoAway")
            self.NextStateTime = int(globalvars.CustomersInfo[self.Type]["goAwayTime"]*1000)
            
        elif state == CustomerState_ThankYou:
            #self.Host.SendCommand(Cmd_TakeOrder)
            self.Animator.SetState("TakeOrder")
            self.NextStateTime = int(globalvars.CustomersInfo[self.Type]["thankYouTime"]*1000)
            
        
    def Show(self, flag = True):
        self.Sprite.visible = flag
        if flag:
            for i in range(self.Hearts):
                self.HeartSprites[i].visible = True
            for i in range(self.Hearts, Const_MaxHearts):
                self.HeartSprites[i].visible = False
        else:
            for i in range(Const_MaxHearts):
                self.HeartSprites[i].visible = False
        
    def Kill(self):
        oE.executor.DismissQueue(self.QueNo)
        self.Animator.Kill()
        self.Sprite.Dispose()
        for spr in self.HeartSprites:
            spr.Dispose()
        del self.HeartSprites
        
    def SendCommand(self, cmd, parameter = None):
        if cmd == Cmd_Customer_SayThankYou:
            self._SetState(CustomerState_ThankYou)
        
    def _OnExecute(self, que):
        try:
            self.NextStateTime -= que.delta
            if self.NextStateTime <= 0:
                if self.State == CustomerState_Ordering:
                    self.Host.SendCommand(Cmd_NewOrder)
                    self._SetState(CustomerState_Wait)
                    
                elif self.State == CustomerState_Wait:
                    if self.Hearts > 1:
                        self.Hearts -= 1
                        self._SetState(CustomerState_Wait)
                    else:
                        self._SetState(CustomerState_GoAway)
                        
                elif self.State == CustomerState_GotGift:
                    self._SetState(CustomerState_Wait)
                    
                elif self.State == CustomerState_GoAway:
                    self._SetState(CustomerState_None)
                    self.Host.SendCommand(Cmd_Station_DeleteCustomer)
                    
                elif self.State == CustomerState_ThankYou:
                    self._SetState(CustomerState_None)
                    self.Host.SendCommand(Cmd_Station_DeleteCustomer)
                    
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        return scraft.CommandStateRepeat
        

#-------------------------------
# ������� �����������
# ��������� ����� ����������� � ��������
#-------------------------------
class CustomersQue(scraft.Dispatcher):
    def __init__(self):
        self.SetState(QueState_None)
        oE.executor.Schedule(self)
        
    def SetState(self, state):
        if state == QueState_Active and self.State != QueState_Active:
            self.NextCustomerTime = randint(globalvars.GameSettings["newcustomertimemin"]*1000,
                                        globalvars.GameSettings["newcustomertimemax"]*1000)
        else:
            self.NextCustomerTime = 0
        self.State = state
        
    def _OnExecute(self, que):
        if self.State == QueState_Active:
            self.NextCustomerTime -= que.delta
            if self.NextCustomerTime <= 0:
                self.SetState(QueState_Passive)
                globalvars.Board.SendCommand(Cmd_NewCustomer)
        return scraft.CommandStateRepeat
        

#-------------------------------
# �������� ����������
#-------------------------------
class CustomersAnimator(scraft.Dispatcher):
    def __init__(self, sprite, animations):
        self.Sprite = sprite
        self.Animations = animations
        self.States = []
        self.QueNo = oE.executor.Schedule(self)
        
    def SetState(self, state):
        if self.Animations[state]["loops"] == 0:
            self.States = [state]
            self.CurrentAnimation = self.Animations[state]["frames"]
            self.Cycling = True
        else:
            self.States.append(state)
            self.CurrentAnimation = self.Animations[state]["frames"]*self.Animations[state]["loops"]
            self.Cycling = False
        self.Fps = self.Animations[state]["fps"]
        self.NextFrameTime = 0
        self.NextFrame = 0
            
    def _OnExecute(self, que):
        try:
            if self.NextFrameTime <= 0:
                if self.NextFrame < len(self.CurrentAnimation) or self.Cycling:
                    self.Sprite.frno = self.CurrentAnimation[self.NextFrame]
                    self.NextFrame = (self.NextFrame + 1) % len(self.CurrentAnimation)
                    self.NextFrameTime += int(1000/self.Fps)
                else:
                    self.SetState(self.States[0])
            self.NextFrameTime -= que.delta
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        return scraft.CommandStateRepeat
        
    def Kill(self):
        oE.executor.DismissQueue(self.QueNo)
        
