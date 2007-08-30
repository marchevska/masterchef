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
from guielements import MakeSimpleSprite, MakeTextSprite, MakeSprite
from extra import Animator, RandomKeyByRates
from random import randint

#------------
# Покупатель; имеет настроение, выраженное в сердечках
# Настроение ухудшается с течением времени
# и улучшается при обслуживании или с помощью предметов
# Если настроение совсем портится (0 сердечек), покупатель уходит
#------------
class Customer(scraft.Dispatcher):
    def __init__(self, type):
        self.Type = type
        self.Sprite = MakeSimpleSprite(globalvars.CustomersInfo.GetSubtag(type).GetStrAttr("src"), Layer_Customer,
                        0, 0, scraft.HotspotCenterBottom)
        self.HilightSprite = MakeSprite("$spritecraft$dummy$", Layer_Customer+1,
                        { "x":0, "y": 0, "parent": self.Sprite, "hotspot": scraft.HotspotCenterBottom })
        self.SpriteProxy = CustomerSpriteProxy(self.Sprite, self.HilightSprite)
        self.Animator = CustomersAnimator(self.SpriteProxy,
                globalvars.CustomerAnimations.GetSubtag(globalvars.CustomersInfo.GetSubtag(type).GetStrAttr("animation"), "Animation"))
        self.HeartSprites = []
        for i in range(Const_MaxHearts):
            self.HeartSprites.append(MakeSimpleSprite("heart", Layer_Recipe,
                        self.Sprite.x + Crd_HeartsDx + i*Crd_HeartSpritesDx,
                        self.Sprite.y + Crd_HeartsDy + i*Crd_HeartSpritesDy))
        self.HasOrder = False
        self.PrevState = CustomerState_None
        self._SetState(CustomerState_Queue)
        self.QueNo = oE.executor.Schedule(self)
        
    def DrawAt(self, x, y):
        self.Sprite.x, self.Sprite.y = x, y
        
    def AttachTo(self, host):
        self.Host = host
        self.Sprite.x, self.Sprite.y = host.CrdX + Crd_CustomerDx, host.CrdY + Crd_CustomerDy
        for i in range(Const_MaxHearts):
            self.HeartSprites[i].x = self.Sprite.x + Crd_HeartsDx + i*Crd_HeartSpritesDx
            self.HeartSprites[i].y = self.Sprite.y + Crd_HeartsDy + i*Crd_HeartSpritesDy
        self._SetHearts(globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("heartsOnStart"))
        self._SetState(CustomerState_Ordering)
        
    def GiveSweet(self):
        self.AddHearts(1)
        self.PrevState = self.State
        self._SetState(CustomerState_GotGift)
        
    def GiveGift(self):
        self.AddHearts(3)
        self.PrevState = self.State
        self._SetState(CustomerState_GotGift)
        
    def AddHearts(self, no):
        self._SetHearts(self.Hearts + no)
        
    def _SetHearts(self, no):
        no = max(0, min(no, Const_MaxHearts))
        if self.State == CustomerState_Queue:
            self.Hearts = no
        elif no>0:
            if self.HeartDecreaseTime <= 0:
                self.HeartDecreaseTime = randint(globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("patientTimeMin")*1000,
                                         globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("patientTimeMax")*1000)
            self.Hearts = no
            for i in range(no):
                self.HeartSprites[i].visible = True
            for i in range(no, Const_MaxHearts):
                self.HeartSprites[i].visible = False
            self.Animator.SetState(str(self.Hearts)+"Hearts")
        else:
            for i in range(Const_MaxHearts):
                self.HeartSprites[i].visible = False
            self._SetState(CustomerState_GoAway)
        
    def _SetState(self, state):
        self.State = state
        if state == CustomerState_Queue:
            self.NextStateTime = 0
            self.HeartDecreaseTime = 0
            self._SetHearts(0)
            self.Animator.SetState("Queue")
            
        elif state == CustomerState_Ordering:
            self.NextStateTime = randint(globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("orderingTimeMin")*1000,
                                         globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("orderingTimeMax")*1000)
            if self.Hearts <= 0:
                self._SetHearts(globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("heartsOnStart"))
            self.Animator.SetState("Order")
            
        elif state == CustomerState_Wait:
            #self.NextStateTime = randint(globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("patientTimeMin")*1000,
            #                             globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("patientTimeMax")*1000)
            self._SetHearts(self.Hearts)
            
        elif state == CustomerState_GotGift:
            self.Animator.SetState("GotGift")
            self.NextStateTime = randint(globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("gotGiftTimeMin")*1000,
                                         globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("gotGiftTimeMax")*1000)
            
        elif state == CustomerState_GoAway:
            self.Host.SendCommand(Cmd_FlopOrder)
            self.Animator.SetState("GoAway")
            self.NextStateTime = int(globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("goAwayTime")*1000)
            
        elif state == CustomerState_MealReady:
            self.Animator.SetState("MealReady")
            self.NextStateTime = int(globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("mealReadyTime")*1000)
            
        elif state == CustomerState_ThankYou:
            #self.Host.SendCommand(Cmd_TakeOrder)
            self.Animator.SetState("TakeOrder")
            self.NextStateTime = int(globalvars.CustomersInfo.GetSubtag(self.Type).GetIntAttr("thankYouTime")*1000)
            
        
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
        
    def Freeze(self, flag):
        self.Animator.Freeze(flag)
        if flag:
            oE.executor.GetQueue(self.QueNo).Suspend()
        else:
            oE.executor.GetQueue(self.QueNo).Resume()
            
    def Hilight(self, flag):
        if flag:
            self.HilightSprite.ChangeKlassTo(globalvars.CustomersInfo.GetSubtag(self.Type).GetStrAttr("hilight"))
        else:
            self.HilightSprite.ChangeKlassTo("$spritecraft$dummy$")
        self.HilightSprite.hotspot = scraft.HotspotCenterBottom
        self.HilightSprite.frno = self.Sprite.frno
        
    def Kill(self):
        oE.executor.DismissQueue(self.QueNo)
        self.Animator.Kill()
        self.Sprite.Dispose()
        for spr in self.HeartSprites:
            spr.Dispose()
        del self.HeartSprites
        
    def SendCommand(self, cmd, parameter = None):
        if cmd == Cmd_Customer_SayThankYou:
            self._SetState(CustomerState_MealReady)
        
    def _OnExecute(self, que):
        try:
            if self.State != CustomerState_Queue:
                if self.State == CustomerState_Wait:
                    self.HeartDecreaseTime -= que.delta
                    if self.HeartDecreaseTime <= 0:
                        self.Hearts -= 1
                        self._SetHearts(self.Hearts)
                        
                else:
                    self.NextStateTime -= que.delta
                    if self.NextStateTime <= 0:
                        if self.State == CustomerState_Ordering:
                            self.Host.SendCommand(Cmd_NewOrder, self._MakeOrder())
                            self._SetState(CustomerState_Wait)
                            
                        elif self.State == CustomerState_GotGift:
                            self._SetState(self.PrevState)
                            #if self.HasOrder:
                            #    self._SetState(CustomerState_Wait)
                            #else:
                            #    self._SetState(CustomerState_Ordering)
                            
                        elif self.State == CustomerState_GoAway:
                            globalvars.Musician.PlaySound("customer.lost")
                            self._SetState(CustomerState_None)
                            self.Host.SendCommand(Cmd_Station_DeleteCustomerAndLoseMoney)
                            
                        elif self.State == CustomerState_MealReady:
                            globalvars.Musician.PlaySound("customer.thankyou")
                            self._SetState(CustomerState_ThankYou)
                            self.Host.SendCommand(Cmd_CustomerGoesAway)
                            
                        elif self.State == CustomerState_ThankYou:
                            self._SetState(CustomerState_None)
                            self.Host.SendCommand(Cmd_Station_DeleteCustomer)
                            if not globalvars.GameSettings.GetBoolAttr("autoReleaseCustomer"):
                                self.Host.SendCommand(Cmd_FreeStation)
                    
        except:
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        return scraft.CommandStateRepeat
        
    # сделать заказ
    def _MakeOrder(self):
        globalvars.Musician.PlaySound("customer.putorder")
        
        tmpLevelRecipeRates = dict(map(lambda x: (x.GetStrAttr("type"), x.GetIntAttr("rate")),
            globalvars.LevelSettings.GetTag("RecipeRates").Tags("Recipe")))
        tmpActualRates = globalvars.BlackBoard.Inspect(BBTag_Recipes)
        for rcp in tmpLevelRecipeRates.keys():
            if not tmpActualRates.has_key(rcp):
                tmpActualRates[rcp] = 0
        tmpAlignedRates = AlignRates(tmpLevelRecipeRates, tmpActualRates)
        
        if globalvars.CustomersInfo.GetSubtag(self.Type).GetStrAttr("dislikes") != "nothing":
            #плохие ингредиенты - те, которые покупатель не любит
            tmpBadIngredients = map(lambda y: y.GetContent(),
                                    filter(lambda x: x.GetStrAttr("type") == globalvars.CustomersInfo.GetSubtag(self.Type).GetStrAttr("dislikes"),
                                    globalvars.CuisineInfo.GetTag("Ingredients").Tags()))
            #хорошие рецепты - не используют плохих ингредиентов
            tmpGoodRecipes = filter(lambda x: \
                filter(lambda y: y in tmpBadIngredients,
                        eval(globalvars.RecipeInfo.GetSubtag(x).GetStrAttr("requires")).keys()) == [],
                        tmpAlignedRates.keys())
            tmpGoodRecipeRates = dict(map(lambda x: (x, tmpAlignedRates[x]), tmpGoodRecipes))
        else:
            tmpGoodRecipeRates = tmpAlignedRates
        
        if SumRates(tmpGoodRecipeRates) == 0:
            for tmp in tmpGoodRecipeRates.keys():
                if tmpLevelRecipeRates[tmp] != 0:
                    tmpGoodRecipeRates[tmp] = 1
        self.HasOrder = True
        tmpOrder = RandomKeyByRates(tmpGoodRecipeRates)
        globalvars.BlackBoard.Update(BBTag_Recipes, { "type": tmpOrder, "delta": 1 })
        return tmpOrder
        
#-------------------------------
# p - ideal rates
# r - actual rates
#-------------------------------
def SumRates(dict):
    return reduce(lambda a,b: a+b, dict.values(),0)
    
def AlignRates(p, r):
    a = 2
    b = -1
    tmpPSum = SumRates(p)
    tmpRSum = SumRates(r)
    if tmpRSum == 0:
        return dict(p)
    else:
        t = {}
        for tmp in p.keys():
            t[tmp] = max(a*tmpRSum*p[tmp] + b*tmpPSum*r[tmp], 0)
        return t

#-------------------------------
# Очередь покупателей
# Выпускает новых покупателей к столикам
#-------------------------------
class CustomersQue(scraft.Dispatcher):
    def __init__(self, theme, x, y):
        self.X0, self.Y0 = x, y
        #список покупателей и их заказов
        #обеспечиваем, чтобы не было более двух одинаовых покупателей подряд!
        self.CustomersList = []
        for i in range(globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("noCustomers")):
            tmpRates = dict(map(lambda x: (x.GetStrAttr("type"), x.GetIntAttr("rate")),
                       globalvars.LevelSettings.GetTag("CustomerRates").Tags("Customer")))
            if i>=2:
                if self.CustomersList[i-2] == self.CustomersList[i-1]:
                    if len(filter(lambda x: tmpRates[x]>0, tmpRates.keys())) > 1:
                        tmpRates.pop(self.CustomersList[i-1])
            self.CustomersList.append(RandomKeyByRates(tmpRates))
            
        self.Customers = map(lambda x: Customer(x), self.CustomersList)
        self._Draw()
        self.SetState(QueState_None)
        self.QueNo = oE.executor.Schedule(self)
        
    def _Draw(self):
        for i in range(min(len(self.Customers), Const_VisibleCustomers)):
            self.Customers[i].DrawAt(self.X0 + i*Crd_QueueCustomerDx, self.Y0 + i*Crd_QueueCustomerDy)
            self.Customers[i].Show(True)
        for i in range(Const_VisibleCustomers, len(self.Customers)):
            self.Customers[i].Show(False)
        
    def HasCustomers(self):
        return (self.RemainingCustomers > 0)
        
    def PopCustomer(self):
        tmp = self.Customers.pop(0)
        self._Draw()
        return tmp
        
    def SetState(self, state):
        if state == QueState_Active and self.State != QueState_Active:
            self.NextCustomerTime = randint(globalvars.GameSettings.GetIntAttr("newCustomerTimeMin")*1000,
                                        globalvars.GameSettings.GetIntAttr("newCustomerTimeMax")*1000)
        else:
            self.NextCustomerTime = 0
        self.State = state
        
    def _OnExecute(self, que):
        #создать нового покупателя и разместить его у столика
        if self.State == QueState_Active:
            self.NextCustomerTime -= que.delta
            if self.NextCustomerTime <= 0:
                self.SetState(QueState_Passive)
                globalvars.Board.SendCommand(Cmd_NewCustomer)
        return scraft.CommandStateRepeat
        
    def Show(self, flag):
        for tmp in self.Customers:
            tmp.Show(flag)
        
    def Freeze(self, flag):
        if flag:
            oE.executor.GetQueue(self.QueNo).Suspend()
        else:
            oE.executor.GetQueue(self.QueNo).Resume()
        for tmp in self.Customers:
            tmp.Freeze(flag)
        
    def Kill(self):
        oE.executor.DismissQueue(self.QueNo)
        for tmp in self.Customers:
            tmp.Kill()
            del tmp
    
#-------------------------------
# Главгерой
# Копия героя приаттачивается к каждому стейшену
# При выдаче заказа покупателю герой показывается 
# на время выдачи, а потом прячется
#-------------------------------
class Hero:
    def __init__(self, x, y):
        self.Sprite = MakeSimpleSprite(u"hero", Layer_Hero, x, y, scraft.HotspotCenterBottom)
        self.Animator = CustomersAnimator(self.Sprite, globalvars.CustomerAnimations.GetSubtag("animation.hero"))
        self.Animator.SetState("None")
        
    def ShowUp(self):
        self.Show(True)
        self.Animator.SetState("GiveOrder")
            
    def Show(self, flag = True):
        self.Sprite.visible = flag
        
        
#-------------------------------
# Анимация персонажа
# Класс управляет переключением и показом анимаций 
# Этот класс при создании получает ноду
# со списокм анимаций: название анимации,
# список кадров и заданные длительности каждого кадра
# Можно задать ограниченное количество циклов или неограниченное (=0)
# см. файл animations.def
#-------------------------------
class CustomersAnimator(scraft.Dispatcher):
    def __init__(self, sprite, animations):
        self.Sprite = sprite
        self.Animations = animations
        self.States = []
        self.QueNo = oE.executor.Schedule(self)
        
    def SetState(self, state):
        if self.Animations.GetSubtag(state).GetIntAttr("loops") == 0:
            self.States = [state]
            self.CurrentAnimation = eval(self.Animations.GetSubtag(state).GetStrAttr("frames"))
            self.Cycling = True
        else:
            self.States.append(state)
            self.CurrentAnimation = eval(self.Animations.GetSubtag(state).GetStrAttr("frames"))*self.Animations.GetSubtag(state).GetIntAttr("loops")
            self.Cycling = False
        self.NextFrameTime = 0
        self.NextFrame = 0
        self.Sprite.frno = self.CurrentAnimation[self.NextFrame][0]
            
    def _OnExecute(self, que):
        try:
            if self.NextFrameTime <= 0:
                if self.NextFrame < len(self.CurrentAnimation) or self.Cycling:
                    self.Sprite.frno = self.CurrentAnimation[self.NextFrame][0]
                    tmpNextFrameData = self.CurrentAnimation[self.NextFrame]
                    if len(tmpNextFrameData) == 2:
                        self.NextFrameTime += tmpNextFrameData[1]
                    else:
                        self.NextFrameTime += randint(tmpNextFrameData[1], tmpNextFrameData[2])
                    self.NextFrame = (self.NextFrame + 1) % len(self.CurrentAnimation)
                else:
                    self.SetState(self.States[0])
            self.NextFrameTime -= que.delta
        except:
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        return scraft.CommandStateRepeat
        
    def Kill(self):
        oE.executor.DismissQueue(self.QueNo)
        
    def Freeze(self, flag):
        if flag:
            oE.executor.GetQueue(self.QueNo).Suspend()
        else:
            oE.executor.GetQueue(self.QueNo).Resume()
            
#------------
# Прокси: покупатель с тенью
# Контролирует два спрайта, 
# у обоих frno должен меняться одинаково!
#------------

class CustomerSpriteProxy(object):
    def __init__(self, mainSprite, secondSprite):
        self.mainSprite = mainSprite
        self.secondSprite = secondSprite
        
    def SetFrno(self, value):
        self.mainSprite.frno = value
        self.secondSprite.frno = value
        
    def GetFrno(self):
        return self.mainSprite.frno
        
    frno = property(GetFrno, SetFrno)
        
