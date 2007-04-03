#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Customer station and supporting classes
"""

import scraft
from scraft import engine as oE
import globalvars
from customer import Customer, Hero
from constants import *
from configconst import *
from guielements import MakeSimpleSprite, MakeDummySprite, PushButton
from extra import *

#---------------------------------------------
# Блок из кастомера и заказа
#---------------------------------------------

class CustomerStation(scraft.Dispatcher):
    def __init__(self, newX, newY, theme):
        self.HasOrder = False
        self.Active = False
        self.MealReady = False
        self.CrdX, self.CrdY = newX, newY
        self.NeededIndicators = []
        self.Dummy = MakeDummySprite(self, Cmd_CustomerStation, newX + Crd_StationDummyDx, newY + Crd_StationDummyDy,
                                     Crd_StationDummyWidth, Crd_StationDummyHeight, Layer_Station)
        self.TableSprite = MakeSimpleSprite(theme["station"], Layer_Station, self.CrdX, self.CrdY)
        self.RecipeIndicator = BarIndicator(self.CrdX + Crd_RecipeSpriteDx, self.CrdY + Crd_RecipeSpriteDy, 52, 46,
                    u"$spritecraft$dummy$", u"$spritecraft$dummy$", Layer_Recipe, True, True)
        self.RecipeIndicator.Show(False)
        self.RecipeInfoSprite = MakeSimpleSprite(theme["recipeInfo"], Layer_Station,
                                    self.CrdX + Crd_RecipeInfoSpriteDx, self.CrdY + Crd_RecipeInfoSpriteDy)
        self.RecipeInfoSprite.visible = False
        self.ReleaseButton = PushButton("", self, Cmd_ReleaseCustomer, PState_Game,
                u"release-button", [0, 1, 2], Layer_PopupBtnTxt, newX + Crd_ReleaseButtonDx, newY + Crd_ReleaseButtonDy, 40, 30)
        self.ReleaseButton.Show(False)
        self.Hero = Hero(self.CrdX + Crd_HeroDx, self.CrdY + Crd_HeroDy)
        self.Hero.Show(False)
        self.State = CStationState_None
        
    def SetState(self, state):
        self.State = state
        
    #--------------
    # сажаем покупателя за столик
    #--------------
    def AttachCustomer(self, customer):
        self.Customer = customer
        customer.AttachTo(self)
        self.Active = True
        
    #--------------
    # "type" - название рецепта 
    #--------------
    def PutOrder(self, type):
        self.HasOrder = True
        self.MealReady = False
        self.OrderType = type
        self.RecipeInfoSprite.visible = True
        self.RecipeIndicator.Show(True)
        self.RecipeIndicator.SetKlasses(globalvars.CuisineInfo["Recipes"][type]["src"],
                                        globalvars.CuisineInfo["Recipes"][type]["emptySrc"])
        self.RecipeIndicator.SetValue(0)
        tmpIng = globalvars.CuisineInfo["Recipes"][type]["requires"].keys()
        self.TokensNeeded = map(lambda x: { "item": x, "no": globalvars.CuisineInfo["Recipes"][type]["requires"][x] }, tmpIng)
        self.TotalRequired = reduce(lambda x, y: x+y["no"], self.TokensNeeded, 0)
        for i in range(len(self.TokensNeeded)):
            self.NeededIndicators.append(NeededIndicator(self.CrdX + Crd_Indicator_DeltaX,
                self.CrdY + Crd_Indicator_DeltaY + i*Crd_IndicatorSign_DeltaY, Layer_Recipe, 
                globalvars.CuisineInfo["Ingredients"][self.TokensNeeded[i]["item"]]["iconSrc"],
                u"arial18", u"galka", self.TokensNeeded[i]["no"]))
        
    #--------------
    # удалить заказ
    #--------------
    def _RemoveOrder(self):
        self.HasOrder = False
        self.RecipeIndicator.Show(False)
        self.RecipeInfoSprite.visible = False
        for tmp in self.NeededIndicators:
            tmp.Kill()
        self.NeededIndicators = []
        self.TokensNeeded = []
        self.ReleaseButton.Show(False)
    
    #--------------
    # добавить "no" токенов типа "food" + проверки
    #--------------
    def AddTokens(self, food, no):
        #tmp - номер нужного ингредиента, для обновления индикаторов
        tmp = filter(lambda x: self.TokensNeeded[x]["item"] == food, range(len(self.TokensNeeded)))
        
        tmpScoreMultiplier = 1
        
        #добавление ингредиентов
        if tmp != []:
            tmpOld = self.TokensNeeded[tmp[0]]["no"]
            tmpNew = max(tmpOld - no, 0)
            self.TokensNeeded[tmp[0]]["no"] = tmpNew
            self.NeededIndicators[tmp[0]].SetValue(tmpNew)
            tmpScoreMultiplier *= 2
            #если закончен один из компонентов рецепта
            if tmpNew == 0 and tmpOld != 0:
                self.Customer.AddHearts(1)
            
        #проверить, готов ли рецепт !!!!
        tmpRemaining = reduce(lambda a,b: a+b["no"], self.TokensNeeded, 0)
        if tmpRemaining == 0 or \
            (tmpRemaining <= globalvars.CuisineInfo["Recipes"][self.OrderType]["readyAt"] and \
            globalvars.CustomersInfo[self.Customer.Type]["takesIncompleteOrder"]):
            self.ReleaseButton.Show(True)
        if tmpRemaining == 0:
            self.MealReady = True
            
        self.RecipeIndicator.SetValue(1.0 - 1.0*tmpRemaining/self.TotalRequired)
            
        #проверить - является ли ингредиент нелюбимым для покуаптеля
        if globalvars.CustomersInfo[self.Customer.Type]["dislikes"] == food:
            self.Customer.AddHearts(-1)
        #если ингредиент не требуется и покупатель требует четкого соблюдения рецепта
        elif tmp == [] and not globalvars.CustomersInfo[self.Customer.Type]["allowsExcessIngredients"]:
            self.Customer.AddHearts(-1)
        
        #проверить - является ли ингредиент любимым для покуаптеля
        if globalvars.CustomersInfo[self.Customer.Type]["likes"] == food:
            tmpScoreMultiplier *= 2
            
        return no*tmpScoreMultiplier
        
    def _OnMouseOver(self, sprite, flag):
        if globalvars.StateStack[-1] == PState_Game:
            if sprite.cookie == Cmd_CustomerStation and self.Active:
                self._Hilight(flag)    
        
    def _OnMouseClick(self, sprite, button, x, y):
        if globalvars.StateStack[-1] == PState_Game:
            if sprite.cookie == Cmd_CustomerStation and self.Active:
                globalvars.Board.SendCommand(Cmd_ClickStation, {"station": self, "hasOrder": self.HasOrder,
                                                            "mealReady": self.MealReady})
        
    def _Hilight(self, flag):
        self.Customer.Hilight(flag)
        if flag:
            self.TableSprite.frno = 1
        else:
            self.TableSprite.frno = 0
        
    def Show(self, flag):
        self.Dummy.visible = flag
        self.TableSprite.visible = flag
        self.RecipeInfoSprite.visible = flag
        self.Hero.Show(False)
        self.ReleaseButton.Show(False)
        if flag and self.HasOrder and self.Active:
            self.AddTokens("", 0)
        if self.Active:
            self.Customer.Show(flag)
        #else:
        #    self.Customer.Show(False)
        for tmp in self.NeededIndicators:
            tmp.Show(flag)
        
    def Freeze(self, flag):
        if self.Active:
            self.Customer.Freeze(flag)
            
    def SendCommand(self, cmd, parameter = None):
        if cmd == Cmd_NewOrder:
            self.PutOrder(parameter)
            
        elif cmd == Cmd_ReleaseCustomer:
            self._RemoveOrder()
            self.Hero.ShowUp()
            self.Customer.SendCommand(Cmd_Customer_SayThankYou)
            self.Active = False
            globalvars.Board.SendCommand(Cmd_CustomerServed)
            
        elif cmd == Cmd_FlopOrder:
            self._RemoveOrder()
            self.Active = False
            print "flop order!"
            globalvars.Board.SendCommand(Cmd_CustomerLost)
            
        elif cmd == Cmd_Station_DeleteCustomer:
            self.Active = False
            self.Customer.Kill()
            self.Hero.Show(False)
            self.State = CStationState_Free
            globalvars.Board.SendCommand(Cmd_FreeStation)
        
    def Kill(self):
        if self.Active:
            self.Customer.Kill()
            del self.Customer
        self.Dummy.Dispose()
        self.TableSprite.Dispose()
        self.RecipeIndicator.Kill()
        self.RecipeInfoSprite.Dispose()
        self.ReleaseButton.Kill()
        for tmp in self.NeededIndicators:
            tmp.Kill()
        
        
#---------------------------------------------
# Индикатор количества требуемых ингредиентов
# Показывает цифру или галочку
#---------------------------------------------

class NeededIndicator:
    def __init__(self, newX, newY, newLayer, tokenKlass, textKlass, checkerKlass, newValue):
        self.TokenSprite = MakeSimpleSprite(tokenKlass, newLayer, newX, newY)
        self.ValueTextSprite = MakeTextSprite(textKlass, newLayer, newX + Crd_IndicatorText_DeltaX, newY, scraft.HotspotLeftCenter)
        self.Checkersprite = MakeSimpleSprite(checkerKlass, newLayer, newX + Crd_IndicatorText_DeltaX, newY)
        #self.TokenSprite.xScale, self.TokenSprite.yScale = Crd_IndicatorScaleXY, Crd_IndicatorScaleXY
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
        
