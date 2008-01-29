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

import gamegui

#---------------------------------------------
# Блок из кастомера и заказа
#---------------------------------------------

class CustomerStation(scraft.Dispatcher):
    def __init__(self, newX, newY, theme):
        self.HasOrder = False
        self.Active = False
        self.MealReady = False
        self.CrdX, self.CrdY = newX, newY
        self.TokensNeeded = []
        self.NeededIndicators = []
        self.Dummy = MakeDummySprite(self, Cmd_CustomerStation, newX + Crd_StationDummyDx, newY + Crd_StationDummyDy,
                                     Crd_StationDummyWidth, Crd_StationDummyHeight, Layer_Station)
        self.TableSprite = MakeSimpleSprite(theme.GetStrAttr("station"), Layer_Station, self.CrdX, self.CrdY)
        self.MaskSprite = MakeSimpleSprite(theme.GetStrAttr("stationMask"), Layer_RecipeFrame,
                                           self.CrdX + Crd_RecipeMaskDx, self.CrdY + Crd_RecipeMaskDy)
        self.MaskSprite.visible = False
        self.RecipeIndicator = BarIndicator(self.CrdX + Crd_RecipeSpriteDx, self.CrdY + Crd_RecipeSpriteDy,
                    Crd_RecipeSpriteWidth, Crd_RecipeSpriteHeight,
                    "$spritecraft$dummy$", "$spritecraft$dummy$", Layer_Recipe,
                    theme.GetStrAttr("stationLine"), True, True)
        self.RecipeIndicator.Show(False)
        self.RecipeInfoSprite = MakeSimpleSprite(theme.GetStrAttr("recipeInfo"), Layer_RecipeInfo,
                                    self.CrdX + Crd_RecipeInfoSpriteDx, self.CrdY + Crd_RecipeInfoSpriteDy)
        self.RecipeInfoSprite.visible = False
        self.ReleaseButton = PushButton("", self, Cmd_ReleaseCustomer, PState_Game,
                "release-button", [0, 1, 2], Layer_Recipe-1, newX + Crd_ReleaseButtonDx, newY + Crd_ReleaseButtonDy, 40, 30)
        self.MoneyButton = PushButton("", self, Cmd_TakeMoney, PState_Game,
                "money-button", [0, 1, 2], Layer_Recipe-1, newX, newY, 60, 60)
        self.MoneyButton.SetSound("customer.takemoney")
        self.ReleaseButton.Show(False)
        self.MoneyButton.Show(False)
        self.Hero = Hero(self.CrdX + Crd_HeroDx, self.CrdY + Crd_HeroDy)
        self.Hero.Show(False)
        self.Customer = None
        self.Tips = 0
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
        #if self.Dummy.mouseOver and globalvars.StateStack[-1] == PState_Game:
        if self.Dummy.mouseOver and not globalvars.Board.Frozen:
            self._Hilight(True)
        else:
            self._Hilight(False)
        globalvars.BlackBoard.Update(BBTag_Hints, { "event": "Customer."+customer.Type,
                                                   "where": (self.CrdX, self.CrdY) })
        
    #--------------
    # "type" - название рецепта 
    #--------------
    def PutOrder(self, type):
        self.HasOrder = True
        self.MealReady = False
        self.OrderType = type
        self.RecipeInfoSprite.visible = True
        self.RecipeIndicator.Show(True)
        self.RecipeIndicator.SetKlasses(globalvars.RecipeInfo.GetSubtag(type).GetStrAttr("src"),
                                        globalvars.RecipeInfo.GetSubtag(type).GetStrAttr("emptySrc"))
        self.RecipeIndicator.SetValue(0)
        self.MaskSprite.visible = True
        tmpReq = eval(globalvars.RecipeInfo.GetSubtag(type).GetStrAttr("requires"))
        self.TokensNeeded = map(lambda x: { "item": x, "no": tmpReq[x] }, tmpReq.keys())
        self.TotalRequired = reduce(lambda x, y: x+y["no"], self.TokensNeeded, 0)
        for i in range(len(self.TokensNeeded)):
            self.NeededIndicators.append(NeededIndicator(self.CrdX + Crd_Indicator_DeltaX,
                self.CrdY + Crd_Indicator_DeltaY + i*Crd_IndicatorSign_DeltaY, Layer_Indicators, 
                globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(self.TokensNeeded[i]["item"]).GetStrAttr("iconSrc"),
                "domcasual-10-up", "galka", self.TokensNeeded[i]["no"]))
            globalvars.BlackBoard.Update(BBTag_Ingredients,
                { "type": self.TokensNeeded[i]["item"], "delta": self.TokensNeeded[i]["no"] })
        if self.Dummy.mouseOver:
            self._Hilight(True)
        
    #--------------
    # удалить заказ
    #--------------
    def _RemoveOrder(self):
        self.HasOrder = False
        self.RecipeIndicator.Show(False)
        self.RecipeInfoSprite.visible = False
        self.MaskSprite.visible = False
        for tmp in self.NeededIndicators:
            tmp.Kill()
        self.NeededIndicators = []
        self.TokensNeeded = []
        self.ReleaseButton.Show(False)
    
    #--------------
    # проверка - можно ли к данному заказу добавить текущий тип ингредиентов с курсора
    #--------------
    def CanAddTokens(self):
        if globalvars.GameSettings.GetBoolAttr("allowExtraIngredients"):
            return True
        else:
            tmp = filter(lambda x: self.TokensNeeded[x]["item"] == gamegui.GetCursorState("tokentype"),
                    range(len(self.TokensNeeded)))
            if tmp == []:
                return False
            elif self.TokensNeeded[tmp[0]]["no"] <= 0:
                return False
            else:
                return True
        
    #--------------
    # добавить "no" токенов типа "food" + проверки
    #--------------
    def AddTokens(self):
        food = gamegui.GetCursorState("tokentype")
        no = gamegui.GetCursorState("tokenno")
        #tmp - номер нужного ингредиента, для обновления индикаторов
        tmp = filter(lambda x: self.TokensNeeded[x]["item"] == food, range(len(self.TokensNeeded)))
        
        #tmpScoreMultiplier = 1
        
        #добавление ингредиентов
        if tmp != []:
            tmpOld = self.TokensNeeded[tmp[0]]["no"]
            tmpNew = max(tmpOld - no, 0)
            self.TokensNeeded[tmp[0]]["no"] = tmpNew
            self.NeededIndicators[tmp[0]].SetValue(tmpNew)
            #tmpScoreMultiplier *= 2
            #если закончен один из компонентов рецепта
            if tmpNew == 0 and tmpOld > 0 and globalvars.GameSettings.GetIntAttr("heartsPerCompletedIngredient") > 0:
                self.Customer.AddHearts(globalvars.GameSettings.GetIntAttr("heartsPerCompletedIngredient"))
            globalvars.BlackBoard.Update(BBTag_Ingredients,
                { "type": food, "delta": tmpNew - tmpOld })
            
        #проверить, готов ли рецепт
        #рецепт готов, если: он полностью выполнен, либо
        #разрешены неполные рецепты и готово достаточное кол-во ингредиентов
        tmpRemaining = reduce(lambda a,b: a+b["no"], self.TokensNeeded, 0)
        if tmpRemaining == 0 or \
                (tmpRemaining <= globalvars.RecipeInfo.GetSubtag(self.OrderType).GetIntAttr("readyAt") and \
                globalvars.CustomersInfo.GetSubtag(self.Customer.Type).GetBoolAttr("takesIncompleteOrder")) and \
                not globalvars.GameSettings.GetBoolAttr("exactRecipes"):
            if globalvars.GameSettings.GetIntAttr("heartsPerCompletedOrder") > 0:
                self.Customer.AddHearts(globalvars.GameSettings.GetIntAttr("heartsPerCompletedOrder"))
            if globalvars.GameSettings.GetBoolAttr("autoReleaseCustomer"):
                self.SendCommand(Cmd_ReleaseCustomer)
                #self.MoneyButton.Show(True)
            else:
                self.ReleaseButton.Show(True)
            
            #спецэффект - контур вокруг силуэта рецепта
            gamegui.ShowGameEffect("Trail.OrderComplete", (self.CrdX, self.CrdY))
            
        if tmpRemaining == 0:
            self.MealReady = True
            
        self.RecipeIndicator.SetValue(1.0 - 1.0*tmpRemaining/self.TotalRequired)
            
        #проверить - является ли ингредиент нелюбимым для покупателя
        if globalvars.CustomersInfo.GetSubtag(self.Customer.Type).GetStrAttr("dislikes") == food:
            self.Customer.AddHearts(-1)
        #если ингредиент не требуется и покупатель требует четкого соблюдения рецепта
        elif tmp == [] and not globalvars.CustomersInfo.GetSubtag(self.Customer.Type).GetBoolAttr("allowsExcessIngredients"):
            self.Customer.AddHearts(-1)
        
        #return eval(globalvars.GameSettings.GetStrAttr("tokenScores"))[min(no, globalvars.GameSettings.GetIntAttr("tokensGroupMax"))]
        return eval(globalvars.GameSettings.GetStrAttr("tokenScores"))[tmpOld - tmpNew]
        
    def _OnMouseOver(self, sprite, flag):
        #if globalvars.StateStack[-1] == PState_Game and self.State != CStationState_None:
        if not globalvars.Board.Frozen and self.State != CStationState_None:
            if sprite.cookie == Cmd_CustomerStation and self.Customer != None:
                self._Hilight(flag)    
        
    def _OnMouseDown(self, sprite, x, y, button):
        if button == 1:
            if (gamegui.GetCursorState("state") == "Token" and self.CanAddTokens()) or \
                        (gamegui.GetCursorState("state") == "Tool" and \
                        gamegui.GetCursorState("tooltype") in ('bonus.sweet', 'bonus.gift')):
                gamegui.SetCursorState({"button": "Down"})
        elif button == 2:
            globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
            
    def _OnMouseUp(self, sprite, x, y, button):
        if button == 1:
            #if (gamegui.GetCursorState("state") == "Token" and self.CanAddTokens()) or \
            #            gamegui.GetCursorState("state") == "Tool" and \
            #            gamegui.GetCursorState("tooltype") in ('bonus.sweet', 'bonus.gift')):
            #    gamegui.SetCursorState({"button": "Roll"})
            #else:
                gamegui.SetCursorState({"button": "Up"})
        #if globalvars.StateStack[-1] == PState_Game:
        if not globalvars.Board.Frozen:
            if sprite.cookie == Cmd_CustomerStation and self.Active:
                globalvars.Board.SendCommand(Cmd_ClickStation, {"station": self, "hasOrder": self.HasOrder,
                                                            "mealReady": self.MealReady})
    #def _OnMouseClick(self, sprite, button, x, y):
    #    if globalvars.StateStack[-1] == PState_Game:
    #        if sprite.cookie == Cmd_CustomerStation and self.Active:
    #            globalvars.Board.SendCommand(Cmd_ClickStation, {"station": self, "hasOrder": self.HasOrder,
    #                                                        "mealReady": self.MealReady})
        
    def _Hilight(self, flag):
        if self.Customer != None:
            self.Customer.Hilight(flag)
        if flag:
            self.TableSprite.frno = 1
            self.MaskSprite.frno = 1
        else:
            self.TableSprite.frno = 0
            self.MaskSprite.frno = 0
        if gamegui.GetCursorState("state") in ("Tool", "Token"):
            if not flag or \
                    (gamegui.GetCursorState("state") == "Token" and self.CanAddTokens()) or \
                    (gamegui.GetCursorState("state") == "Tool" and \
                    gamegui.GetCursorState("tooltype") in ('bonus.sweet', 'bonus.gift')):
                self.Customer.Sprite.cfilt.color = CFilt_White
                self.TableSprite.cfilt.color = CFilt_White
                self.MaskSprite.cfilt.color = CFilt_White
                self.RecipeInfoSprite.cfilt.color = CFilt_White
                gamegui.SetCursorState({"red": False})
                if flag:
                    gamegui.SetCursorState({"button": "Roll"})
                else:
                    gamegui.SetCursorState({"button": "Up"})
            else:
                self.Customer.Sprite.cfilt.color = CFilt_Red
                self.TableSprite.cfilt.color = CFilt_Red
                self.MaskSprite.cfilt.color = CFilt_Red
                self.RecipeInfoSprite.cfilt.color = CFilt_Red
                gamegui.SetCursorState({"button": "Up", "red": True })
        elif gamegui.GetCursorState("state") == "Empty":
            gamegui.SetCursorState({"button": "Up"})
        
    def Show(self, flag):
        self.Dummy.visible = flag
        self.TableSprite.visible = flag
        self.RecipeInfoSprite.visible = flag
        self.Hero.Show(False)
        self.ReleaseButton.Show(False)
        if flag and self.HasOrder and self.Active:
            self.MaskSprite.visible = False
            self.AddTokens("", 0)
        else:
            self.MaskSprite.visible = True
        if self.Active:
            self.Customer.Show(flag)
        #else:
        #    self.Customer.Show(False)
        for tmp in self.NeededIndicators:
            tmp.Show(flag)
        
    def Freeze(self, flag):
        #if self.Active:
        if self.Customer != None:
            self.Customer.Freeze(flag)
            
    def SendCommand(self, cmd, parameter = None):
        if cmd == Cmd_NewOrder:
            self.PutOrder(parameter)
            
        elif cmd == Cmd_ReleaseCustomer:
            globalvars.Board.SendCommand(Cmd_CustomerServed)
            self.Tips = eval(globalvars.CustomersInfo.GetSubtag(self.Customer.Type).GetStrAttr("tips"))[self.Customer.Hearts]
            self.Customer.SendCommand(Cmd_Customer_SayThankYou)
            self.Active = False
            
        elif cmd == Cmd_CustomerGoesAway:
            self._RemoveOrder()
            self.Hero.ShowUp()
            
        elif cmd == Cmd_FlopOrder:
            self._RemoveOrder()
            self.Active = False
            globalvars.Board.SendCommand(Cmd_CustomerLost)
            
        elif cmd == Cmd_Station_DeleteCustomer:
            self.Active = False
            if self.Dummy.mouseOver:
                self._Hilight(False)
            self.Customer.Kill()
            self.Customer = None
            self.Hero.Show(False)
            if globalvars.GameSettings.GetBoolAttr("autoReleaseCustomer"):
                self.MoneyButton.Show(True)
            
        elif cmd == Cmd_FreeStation:
            self.MoneyButton.Show(False)
            self.State = CStationState_Free
            globalvars.Board.SendCommand(Cmd_FreeStation)
            
        elif cmd == Cmd_TakeMoney:
            self.MoneyButton.Show(False)
            self.State = CStationState_Free
            globalvars.Board.SendCommand(Cmd_FreeStation)
            globalvars.Board.SendCommand(Cmd_TakeMoney, { "station": self,
                        "amount": globalvars.RecipeInfo.GetSubtag(self.OrderType).GetIntAttr("price"),
                        "tips": self.Tips})
            globalvars.BlackBoard.Update(BBTag_Hints, { "event": "Station.TakeMoney",
                                                   "where": (self.CrdX, self.CrdY) })
            
        elif cmd == Cmd_Station_DeleteCustomerAndLoseMoney:
            self.Active = False
            if self.Dummy.mouseOver:
                self._Hilight(False)
            self.Customer.Kill()
            self.Customer = None
            self.Hero.Show(False)
            self.State = CStationState_Free
            globalvars.Board.SendCommand(Cmd_FreeStation)
            globalvars.Board.SendCommand(Cmd_TakeMoney, { "station": self,
                        "amount": -globalvars.GameSettings.GetIntAttr("customerLossPrice") })
            globalvars.BlackBoard.Update(BBTag_Hints, { "event": "Station.LoseMoney",
                                                   "where": (self.CrdX, self.CrdY) })
            
        
    def Kill(self):
        if self.Active:
            self.Customer.Kill()
            self.Customer = None
        self.Dummy.Dispose()
        self.TableSprite.Dispose()
        self.MaskSprite.Dispose()
        self.RecipeIndicator.Kill()
        self.RecipeInfoSprite.Dispose()
        self.ReleaseButton.Kill()
        self.MoneyButton.Kill()
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
        self.Checkersprite.xScale, self.Checkersprite.yScale = Crd_IndicatorScaleXY, Crd_IndicatorScaleXY
        self.SetValue(newValue)
        
    def SetValue(self, value):
        self.Value = value
        self.Show()
        
    def Show(self, flag = True):
        if flag:
            self.TokenSprite.visible = True
            if self.Value > 0:
                self.ValueTextSprite.text = str(self.Value)
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
        
