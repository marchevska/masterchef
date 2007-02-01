#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Customer station and supporting classes
"""

import scraft
from scraft import engine as oE
import globalvars
from customer import Customer
from constants import *
from configconst import *
from guielements import MakeSimpleSprite, MakeDummySprite, PushButton
from extra import *

#---------------------------------------------
# ���� �� ��������� � ������
#---------------------------------------------

class CustomerStation(scraft.Dispatcher):
    def __init__(self, newX, newY):
        self.HasOrder = False
        self.CrdX, self.CrdY = newX, newY
        self.NeededIndicators = []
        self.Dummy = MakeDummySprite(self, Cmd_CustomerStation, newX + Crd_StationDummyDx, newY + Crd_StationDummyDy,
                                     Crd_StationDummyWidth, Crd_StationDummyHeight, Layer_Order)
        self.TableSprite = MakeSimpleSprite(u"table", Layer_Order+1, self.CrdX, self.CrdY)
        self.RecipeInfoSprite = MakeSimpleSprite(u"recipe-info", Layer_Order+1,
                                    self.CrdX + Crd_RecipeInfoSpriteDx, self.CrdY + Crd_RecipeInfoSpriteDy)
        self.RecipeInfoSprite.visible = False
        self.ReleaseButton = PushButton("", self, Cmd_ReleaseCustomer, PState_Game,
                u"release-button", [0, 1, 2], Layer_PopupBtnTxt, newX + Crd_ReleaseButtonDx, newY + Crd_ReleaseButtonDy, 40, 30)
        self.ReleaseButton.Show(False)
        self.State = CStationState_None
        
    def SetState(self, state):
        self.State = state
        
    #--------------
    # "type" - ��� ��������� 
    #--------------
    def AttachCustomer(self, type):
        self.Customer = Customer(type, self)
        
    #--------------
    # "type" - �������� ������� 
    #--------------
    def PutOrder(self, type):
        self.HasOrder = True
        self.OrderType = type
        self.RecipeInfoSprite.visible = True
        self.OrderSprite = MakeSimpleSprite(globalvars.CuisineInfo["Recipes"][type]["src"],
                Layer_Order, self.CrdX + Crd_RecipeSpriteDx, self.CrdY + Crd_RecipeSpriteDy)
        tmpIng = globalvars.CuisineInfo["Recipes"][type]["requires"].keys()
        self.TokensNeeded = map(lambda x: { "item": x, "no": globalvars.CuisineInfo["Recipes"][type]["requires"][x] }, tmpIng)
        for i in range(len(self.TokensNeeded)):
            self.NeededIndicators.append(NeededIndicator(self.CrdX + Crd_Indicator_DeltaX,
                self.CrdY + Crd_Indicator_DeltaY + i*Crd_IndicatorSign_DeltaY, Layer_Tokens, 
                globalvars.CuisineInfo["Ingredients"][self.TokensNeeded[i]["item"]]["src"],
                u"arial18", u"galka", self.TokensNeeded[i]["no"]))
        
    #--------------
    # ������� �����
    #--------------
    def _RemoveOrder(self):
        self.State = CStationState_Free
        self.HasOrder = False
        self.OrderSprite.Dispose()
        self.RecipeInfoSprite.visible = False
        for tmp in self.NeededIndicators:
            tmp.Kill()
        self.NeededIndicators = []
        self.TokensNeeded = []
        self.ReleaseButton.Show(False)
    
    #--------------
    # �������� "no" ������� ���� "food" + ��������
    #--------------
    def AddTokens(self, food, no):
        #tmp - ����� ������� �����������, ��� ���������� �����������
        tmp = filter(lambda x: self.TokensNeeded[x]["item"] == food, range(len(self.TokensNeeded)))
        
        #��������� - �������� �� ���������� ��������� ��� ����������
        if globalvars.CustomersInfo[self.Customer.Type]["dislikes"] == food:
            self.Customer.AddHearts(-1)
        #���� ���������� �� ��������� � ���������� ������� ������� ���������� �������
        elif tmp == [] and not globalvars.CustomersInfo[self.Customer.Type]["allowsExcessIngredients"]:
            self.Customer.AddHearts(-1)
        
        #��������� - �������� �� ���������� ������� ��� ����������
        if globalvars.CustomersInfo[self.Customer.Type]["likes"] == food:
            tmpScoreMultiplier = 2
        else:
            tmpScoreMultiplier = 1
            
        #���������� ������������
        if tmp != []:
            tmpOld = self.TokensNeeded[tmp[0]]["no"]
            tmpNew = max(tmpOld - no, 0)
            self.TokensNeeded[tmp[0]]["no"] = tmpNew
            self.NeededIndicators[tmp[0]].SetValue(tmpNew)
            tmpScoreMultiplier *= 2
            #���� �������� ���� �� ����������� �������
            if tmpNew == 0 and tmpOld != 0:
                self.Customer.AddHearts(1)
            
        #���������, ����� �� ������ !!!!
        tmpRemaining = reduce(lambda a,b: a+b["no"], self.TokensNeeded, 0)
        if tmpRemaining == 0 or \
            (tmpRemaining <= globalvars.CuisineInfo["Recipes"][self.OrderType]["readyAt"] and \
            globalvars.CustomersInfo[self.Customer.Type]["takesIncompleteOrder"]):
            self.ReleaseButton.Show(True)
            
        return no*tmpScoreMultiplier
        
    def _OnMouseClick(self, sprite, button, x, y):
        if sprite.cookie == Cmd_CustomerStation and self.HasOrder:
            globalvars.Board.SendCommand(Cmd_ClickStation, self)
        
    def SendCommand(self, cmd, parameter = None):
        if cmd == Cmd_ReleaseCustomer:
            self.HasOrder = False
            self.Customer.SendCommand(Cmd_Customer_SayThankYou)
            #globalvars.Board.SendCommand(Cmd_ReleaseCustomer, self)
            
        elif cmd == Cmd_NewOrder:
            globalvars.Board.SendCommand(Cmd_NewOrder, self)
            
        elif cmd == Cmd_FlopOrder:
            print "flop order!"
            
        elif cmd == Cmd_Station_DeleteCustomer:
            self.Customer.Kill()
            self._RemoveOrder()
            globalvars.Board.SendCommand(Cmd_FreeStation)
        
#---------------------------------------------
# ��������� ���������� ��������� ������������
# ���������� ����� ��� �������
#---------------------------------------------

class NeededIndicator:
    def __init__(self, newX, newY, newLayer, tokenKlass, textKlass, checkerKlass, newValue):
        self.TokenSprite = MakeSimpleSprite(tokenKlass, newLayer, newX, newY)
        self.ValueTextSprite = MakeTextSprite(textKlass, newLayer, newX + Crd_IndicatorText_DeltaX, newY, scraft.HotspotLeftCenter)
        self.Checkersprite = MakeSimpleSprite(checkerKlass, newLayer, newX + Crd_IndicatorText_DeltaX, newY)
        self.TokenSprite.xScale, self.TokenSprite.yScale = Crd_IndicatorScaleXY, Crd_IndicatorScaleXY
        self.ValueTextSprite.xScale, self.ValueTextSprite.yScale = Crd_IndicatorScaleXY, Crd_IndicatorScaleXY
        self.Checkersprite.xScale, self.Checkersprite.yScale = Crd_IndicatorScaleXY, Crd_IndicatorScaleXY
        self.SetValue(newValue)
        
    def SetValue(self, value):
        self.Value = value
        self.Show()
        
    def Show(self, flag = True):
        if flag:
            self.TokenSprite.visible = True
            if self.Value > 0:
                self.ValueTextSprite.text = unicode(str(self.Value))
                self.ValueTextSprite.visible = True
                self.Checkersprite.visible = False
            else:
                self.ValueTextSprite.visible = False
                self.Checkersprite.visible = True
        else:
            self.TokenSprite.visible = False
            self.ValueTextSprite.visible = False
            self.Checkersprite.visible = False
        
    def Kill(self):
        self.TokenSprite.Dispose()
        self.Checkersprite.Dispose()
        self.ValueTextSprite.Dispose()
        
