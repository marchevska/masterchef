#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef 
Игровое поле
"""

import sys, string, traceback
from random import choice
import scraft
from scraft import engine as oE
from constants import *
from configconst import *
from advisor import Advisor
from customerstation import CustomerStation
from storage import Store, SingularStore, Field, TrashCan, Collapsoid
from conveyor import Conveyor
from blackboard import BlackBoard
from extra import *
from customer import *
import config
import defs
import playerlist
import globalvars
import gamegui

from teggo.games import spriteworks, musicsound

class GameBoard(scraft.Dispatcher):
    
    def __init__(self):
        self.BgSprite = spriteworks.MakeSprite("$spritecraft$dummy$", Layer_GameBg)
        self.DoorSprite = spriteworks.MakeSprite("$spritecraft$dummy$", Layer_Door,
                                { "x": Crd_DoorX, "y": Crd_DoorY, "hotspot": scraft.HotspotCenter })
        self.BgReceptor = spriteworks.MakeSprite("$spritecraft$dummy$", Layer_BgReceptor,
                                { "x": 400, "y": 300, "xSize": 800, "ySize": 600,
                                "hotspot": scraft.HotspotCenter,
                                "dispatcher": self, "cookie": Cmd_BgReceptor })
        
        self.CustomersQue = None
        self.Advisor = None
        self.Fields = []
        self.TrashCans = []
        self.CStations = []
        self.Stores = []
        self.Conveyors = []
        self.Static = []
        self.TokensFrom = None
        self.NoErrors = 0
        self.StationsToOccupy = []
        
        self.Frozen = False
        self.Playing = False
        self.MyRand = oE.NewRandomizer()
        self._SetState(GameState_None)
        gamegui.SetCursorState({"state": "Empty" })
        self.QueNo = oE.executor.Schedule(self)
        self.Show(False)
        self.Freeze(True)
        
    def LaunchLevel(self):
        self.Clear()
        globalvars.BlackBoard.ClearTag(BBTag_Ingredients)
        globalvars.BlackBoard.ClearTag(BBTag_Recipes)
        self.Freeze(False)
        try:
            self.Load()
            self.Expert = False
            gamegui.ResetGameHUD()
            self._UpdateLevelInfo()
        except:
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        
    def ReallyStart(self):
        for tmpStation in self.StationsToOccupy:
            self._NextCustomerTo(tmpStation)
        self.StationsToOccupy = []
        
    def Restart(self):
        self.Clear()
        self.LaunchLevel()
        
        
    #--------------------------
    # Загрузка уровня
    #--------------------------
    def Load(self):
        
        self.Playing = True
        defs.ReadLevelSettings(globalvars.CurrentPlayer.GetLevel().GetContent())
        
        self.LevelScore = 0
        self.CustomersServed = 0
        self.CustomersLost = 0
        self.NoErrors = 0
        
        tmpTheme = globalvars.ThemesInfo.GetSubtag(globalvars.LevelSettings.GetTag("Layout").GetStrAttr(u"theme"))
        self.BgSprite.ChangeKlassTo(tmpTheme.GetStrAttr("background"))
        self.DoorSprite.ChangeKlassTo("$spritecraft$dummy$")
        
        #reset customer dispatcher
        self.RemainingCustomers = globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("noCustomers")
        tmp = globalvars.LevelSettings.GetTag("Layout").GetTag("CustomersQue")
        self.CustomersQue = CustomersQue(tmpTheme, tmp.GetIntAttr("X"), tmp.GetIntAttr("Y"))
        
        #размещение стейшенов 
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("CustomerStation"):
            tmpStation = CustomerStation(tmp.GetIntAttr("x"), tmp.GetIntAttr("y"), tmpTheme)
            if tmp.GetBoolAttr("occupied"):
                self.StationsToOccupy.append(tmpStation)
                #self._NextCustomerTo(tmpStation)
            else:
                tmpStation.SetState(CStationState_Free)
            self.CStations.append(tmpStation)
        
        #игровое поле, размещение складов
        self.Fields = []
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("Field"):
            self.Fields.append(Field(tmp.GetIntAttr("XSize"), tmp.GetIntAttr("YSize"),
                        tmp.GetIntAttr("X0"), tmp.GetIntAttr("Y0"), tmpTheme))
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("Collapsoid"):
            self.Fields.append(Collapsoid(tmp.GetIntAttr("XSize"), tmp.GetIntAttr("YSize"),
                        tmp.GetIntAttr("InitialRows"), tmp.GetIntAttr("SensorAt"), 
                        tmp.GetIntAttr("Delay"), tmp.GetIntAttr("DropIn"),
                        tmp.GetIntAttr("ShiftSpeed"), tmp.GetIntAttr("X0"), tmp.GetIntAttr("Y0"), tmpTheme))
        self.Stores = []
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("Store"):
            if tmp.GetBoolAttr("Multi"):
                self.Stores.append(Store(tmp.GetIntAttr("XSize"), tmp.GetIntAttr("YSize"),
                        tmp.GetIntAttr("X0"), tmp.GetIntAttr("Y0"), tmpTheme))
            else:
                self.Stores.append(SingularStore(tmp.GetIntAttr("XSize"), tmp.GetIntAttr("YSize"),
                        tmp.GetIntAttr("X0"), tmp.GetIntAttr("Y0"), tmpTheme))
                
        
        self.Conveyors = []
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("Conveyor"):
            self.Conveyors.append(Conveyor(tmp.GetIntAttr("X0"), tmp.GetIntAttr("Y0"),
                        tmp.GetIntAttr("Speed"), tmp.GetIntAttr("Delta")))#, tmpTheme))
        
        #прочие объекты
        self.Static = []
        if globalvars.LevelSettings.GetTag("Layout").GetCountTag("Counter")>0:
            self.Static.append(spriteworks.MakeSprite(tmpTheme.GetStrAttr("counter"), Layer_Counter,
                { "x": globalvars.LevelSettings.GetTag("Layout").GetTag("Counter").GetIntAttr("x"),
                "y": globalvars.LevelSettings.GetTag("Layout").GetTag("Counter").GetIntAttr("y"),
                "hotspot": scraft.HotspotCenter }))
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("Decoration"):
            self.Static.append(spriteworks.MakeSprite(tmp.GetStrAttr("type"), Layer_Deco,
                { "x": tmp.GetIntAttr("x"), "y": tmp.GetIntAttr("y"), "hotspot": scraft.HotspotCenter }))
        
        self.TrashCans = []
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("TrashCan"):
            self.TrashCans.append(TrashCan(globalvars.LevelSettings.GetTag("Layout").GetTag("TrashCan").GetIntAttr("size"),
                                globalvars.LevelSettings.GetTag("Layout").GetTag("TrashCan").GetIntAttr("x"),
                                globalvars.LevelSettings.GetTag("Layout").GetTag("TrashCan").GetIntAttr("y"), tmpTheme))
            
        tmpFreeStations = filter(lambda x: x.State == CStationState_Free, self.CStations)
        if tmpFreeStations != []:
            self.CustomersQue.SetState(QueState_Active)
        
        #заполнение поля
        for tmp in self.Fields:
            tmp.InitialFilling()
        
        self.Advisor = Advisor()
        
        self._SetState(GameState_StartLevel)
        gamegui.SetCursorState({"state": "Empty" })
        
        gamegui.UpdateGameHUD()
        
    #--------------------------
    # Поместить следующего покупателя к заданному стейшену
    #--------------------------
    def _NextCustomerTo(self, station):
        station.SetState(CStationState_Busy)
        station.AttachCustomer(self.CustomersQue.PopCustomer())
        self.RemainingCustomers -= 1
        self._UpdateLevelInfo()
        if self.RemainingCustomers <= 0:
            tmpTheme = globalvars.ThemesInfo.GetSubtag(globalvars.LevelSettings.GetTag("Layout").GetStrAttr(u"theme"))
            self.DoorSprite.ChangeKlassTo(tmpTheme.GetStrAttr("door"))
            tmp = globalvars.LevelSettings.GetTag("Layout").GetTag("Door")
        
    def _OnMouseClick(self, sprite, x, y, button):
        if button == 2:
            if sprite.cookie == Cmd_BgReceptor:
                self.SendCommand(Cmd_DropWhatYouCarry)
    
    #--------------------------
    # обработка входящих команд
    #--------------------------
    def SendCommand(self, cmd, parameter = None):
        if cmd == Cmd_MovementFinished:
            if self.State == GameState_StartLevel:
                self._SetState(GameState_Play)
            
        #переполнение коллапсоида - штраф и удаление лишнего
        elif cmd == Cmd_CollapsoidFull:
            tmp = parameter.GetBurnCrd()
            parameter.SendCommand(Cmd_ReselectBeforeBurn)
            parameter.SendCommand(Cmd_CollapsoidBurn)
            #максимальный штраф задан (=10 или около того)
            self.NoErrors = min(self.NoErrors+1, globalvars.GameSettings.GetIntAttr("maxColapsoidErrors"))
            self.AddScore(-self.NoErrors*len(tmp))
            for (x, y) in tmp:
                gamegui.ShowGameText("score", -self.NoErrors, (x, y))
            
        elif cmd == Cmd_ClickStation:
            if gamegui.GetCursorState("state") == "Token":
                if parameter["hasOrder"] and not parameter["mealReady"]:
                    if parameter["station"].CanAddTokens():
                        tmpFrom = self.TokensFrom
                        tmpDeltaScore = parameter["station"].AddTokens()
                        self.AddScore(tmpDeltaScore)
                        if tmpDeltaScore > 0:
                            musicsound.PlaySound("tokens.give")
                            gamegui.ShowGameText("score", tmpDeltaScore, (parameter["station"].CrdX, parameter["station"].CrdY))
                        if tmpFrom.Collapsing:
                            if gamegui.GetCursorState("tokenno") > globalvars.GameSettings.GetIntAttr("tokenForIncreadible"):
                                gamegui.ShowGameText("commend", "Str_Incredible", tmpFrom.GetCentralCrd())
                            elif gamegui.GetCursorState("tokenno") > globalvars.GameSettings.GetIntAttr("tokensForGreat"):
                                gamegui.ShowGameText("commend", "Str_Great", tmpFrom.GetCentralCrd())
                        self.TokensFrom.RemoveTokens()
                        self.SendCommand(Cmd_DropWhatYouCarry)
                        if tmpFrom in self.Fields:
                            tmpFrom.SetState(FieldState_Collapse)
                    
            #иначе - использовать бонус
            elif gamegui.GetCursorState("state") == "Tool":
                if gamegui.GetCursorState("tooltype") in ('bonus.sweet', 'bonus.gift'):
                    if gamegui.GetCursorState("tooltype") == 'bonus.sweet':
                        musicsound.PlaySound("customer.gotgift")
                        parameter["station"].Customer.GiveSweet()
                    elif gamegui.GetCursorState("tooltype") == 'bonus.gift':
                        musicsound.PlaySound("customer.gotgift")
                        parameter["station"].Customer.GiveGift()
                    tmpFrom = self.TokensFrom
                    self.TokensFrom.RemoveTokens()
                    self.SendCommand(Cmd_DropWhatYouCarry)
                    if tmpFrom in self.Fields:
                        tmpFrom.SetState(FieldState_Collapse)
                
        elif cmd == Cmd_ClickStorage:
            if gamegui.GetCursorState("state") == "Tokens":
                if parameter["where"].HasFreeSlots(gamegui.GetCursorState("tokenno")):# and self.TokensFrom == self:
                    tmpFrom = self.TokensFrom
                    tmpType = gamegui.GetCursorState("tokentype")
                    tmpNo = gamegui.GetCursorState("tokenno")
                    tmpFrom.RemoveTokens()
                    self.SendCommand(Cmd_DropWhatYouCarry)
                    parameter["where"].AddTokens(tmpType, tmpNo, parameter["pos"])
                    if tmpFrom in self.Fields:
                        tmpFrom.SetState(FieldState_Collapse)
            
        elif cmd == Cmd_TrashCan:
            if gamegui.GetCursorState("state") == "Token":
                tmpFrom = self.TokensFrom
                tmpNo = gamegui.GetCursorState("tokenno")
                self.TokensFrom.RemoveTokens()
                self._DropTokensTo(tmpFrom)
                parameter.Discard(tmpNo)
                if tmpFrom in self.Fields:
                    tmpFrom.SetState(FieldState_Collapse)
            
        elif cmd == Cmd_DropWhatYouCarry:
            if gamegui.GetCursorState("state") == "Token":
                if self.TokensFrom != None:
                    self._DropTokensTo(self.TokensFrom)
            elif gamegui.GetCursorState("state") == "Tool":
                if self.TokensFrom != None:
                    self._DropPowerUp(self.TokensFrom)
                else:
                    self._DropTool()
            gamegui.SetCursorState({"state": "Empty", "tokentype": "", "tokenno": 0})
            
        elif cmd == Cmd_PickFromStorage:
            self._PickTokensFrom(parameter["where"], parameter["type"], parameter["no"])
            
        elif cmd == Cmd_PickFromConveyor:
            if gamegui.GetCursorState("state") == "Token":
                if self.TokensFrom != None:
                    parameter["where"].SendCommand(Cmd_ReturnToConveyor,
                                    { "type": gamegui.GetCursorState("tokentype"),
                                     "position": parameter["position"] })
            self._PickFromConveyor(parameter["where"], parameter["type"])
            
        elif cmd == Cmd_NewCustomer:
            tmpFreeStations = filter(lambda x: x.State == CStationState_Free, self.CStations)
            self._NextCustomerTo(choice(tmpFreeStations))
            if self.RemainingCustomers > 0 and len(tmpFreeStations) > 1:
                self.CustomersQue.SetState(QueState_Active)
                
        # покупатель успешно обслужен
        elif cmd == Cmd_CustomerServed:
            self.CustomersServed += 1
            #проверить - есть ли еще покупатели, которых надо обслуживать
            if self.CustomersServed+self.CustomersLost == \
                    globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("noCustomers"):
                for tmp in self.Fields:
                    tmp.SendCommand(Cmd_StopDropper)
            
        #покупатель ушел недовольный
        elif cmd == Cmd_CustomerLost:
            self.CustomersLost += 1
            #проверить - есть ли еще покупатели, которых надо обслуживать
            if self.CustomersServed+self.CustomersLost == \
                    globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("noCustomers"):
                for tmp in self.Fields:
                    tmp.SendCommand(Cmd_StopDropper)
                
        elif cmd == Cmd_FreeStation:
            if self.RemainingCustomers > 0:
                self.CustomersQue.SetState(QueState_Active)
                
        elif cmd == Cmd_TakeMoney:
            self.AddScore(parameter["amount"])
            tmpCrd = (parameter["station"].CrdX, parameter["station"].CrdY)
            if parameter.has_key("tips"):
                self.AddScore(parameter["tips"])
                gamegui.ShowGameText("money", (parameter["amount"], parameter["tips"]), tmpCrd)
            else:
                gamegui.ShowGameText("money", (parameter["amount"],), tmpCrd)
            
        elif cmd == Cmd_PickPowerUp:
            self._PickPowerUp(parameter["type"], parameter["where"])
        
        elif cmd == Cmd_UtilizePowerUp:
            if parameter == 'bonus.hearts':
                for tmp in self.CStations:
                    if tmp.Active:
                        tmp.Customer.GiveSweet()
                        
        #экстренное завершение уровня в отладочном режиме
        elif cmd == Cmd_DebugFinishLevel:       
            #self.LevelScore = max(self.LevelScore,
            #    globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("moneygoal"))
            self.LevelScore = max(self.LevelScore,
                globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("expertgoal"))
            self._SetState(GameState_EndLevel)
            
        elif cmd == Cmd_DebugLoseLevel:       
            self._SetState(GameState_EndLevel)
            
        elif cmd == Cmd_DebugLastCustomer:
            if self.RemainingCustomers > 1:
                self.RemainingCustomers = 1 
            
    def AddScore(self, delta):
        tmpOldScore = self.LevelScore
        tmpTextEvent = False
        tmpStr = ""
        
        self.LevelScore = max(self.LevelScore + delta, 0)
        self._UpdateLevelInfo()
        if tmpOldScore <= globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("moneyGoal") <= self.LevelScore:
            tmpTextEvent = True
            tmpStr = "Str_LevelGoalReached"
        elif tmpOldScore <= globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("expertGoal") <= self.LevelScore:
            tmpTextEvent = True
            tmpStr = "Str_ExpertGoalReached"
        if tmpTextEvent:
            gamegui.ShowGameText("goalreached", tmpStr)
            musicsound.PlaySound("level.goalreached")
    
    #--------------------------
    # задает состояние игры
    #--------------------------
    def _SetState(self, state, parameter = None):
        self.State = state
        if state == GameState_None:
            pass
            
        #начало уровня; задать способ появления блоков на поле
        elif state == GameState_StartLevel:
            self.StartTime = oE.millis
            for tmp in self.Fields:
               tmp.SetState(FieldState_StartLevel)
            self._SetState(GameState_Play)
            
        #основной цикл - игра
        elif state == GameState_Play:
            pass
                
        #конец уровня; задать способ удаления блоков с поля
        elif state == GameState_EndLevel:
            for tmp in self.Fields:
                tmp.SetState(FieldState_EndLevel)
            if parameter == False:
                gamegui.ShowLevelResults(False,
                        { "served": self.CustomersServed, "lost": self.CustomersLost, "score": self.LevelScore,
                         "expert": self.LevelScore >= globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("expertgoal") } )
            else:
                #if globalvars.RunMode == RunMode_Play:
                tmpBest = globalvars.BestResults.GetSubtag(globalvars.CurrentPlayer.GetLevel().GetContent())
                if self.LevelScore >= tmpBest.GetIntAttr("hiscore"):
                    config.UpdateBestResults(globalvars.CurrentPlayer.GetLevel().GetContent(),
                        globalvars.GameConfig.GetStrAttr("Player"), self.LevelScore)
                globalvars.CurrentPlayer.RecordLevelResults({"expert": self.LevelScore >= globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("expertgoal"),
                            "hiscore": self.LevelScore, "played": True})
                gamegui.ShowLevelResults((self.LevelScore >= globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("moneygoal")),
                        { "served": self.CustomersServed, "lost": self.CustomersLost, "score": self.LevelScore,
                         "expert": self.LevelScore >= globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("expertgoal") } )
        
        
    #--------------------------
    # основной цикл
    #--------------------------
    def _OnExecute(self, que) :
        try:
            if self.State == GameState_StartLevel:
                pass
                
            elif self.State == GameState_Play:
                #проверка на конец уровня
                if self.RemainingCustomers == 0:
                    tmpBusyStations = filter(lambda x: x.State == CStationState_Busy, self.CStations)
                    if tmpBusyStations == []:
                        self._SetState(GameState_EndLevel)
                
            elif self.State == GameState_EndLevel:
                #красивое падение блоков в конце уровня, по заданной программе
                self._SetState(GameState_None)
            
            #self._UpdateLevelInfo()
            
        except:
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        return scraft.CommandStateRepeat
        
    #--------------------------
    # Подбирает иконку бонуса
    #--------------------------
    def _PickPowerUp(self, type, where):
        self.SendCommand(Cmd_DropWhatYouCarry)
        gamegui.SetCursorState({"state": "Tool", "tooltype": type})
        self.TokensFrom = where
    
    #--------------------------
    # Сбрасывает иконку бонуса (тулза)
    #--------------------------
    def _DropPowerUp(self, where):
        if where != None:
            where.DropTokens()
        gamegui.SetCursorState({"state": "Empty"})
        self.TokensFrom = None
        
    def _PickFromConveyor(self, where, type):
        gamegui.SetCursorState({"state": "Token", "tokentype": type, "tokenno": 1 })
        self.TokensFrom = where
        musicsound.PlaySound("tokens.pick")
        
    def _PickTokensFrom(self, where, type, no):
        gamegui.SetCursorState({"state": "Token", "tokentype": type, "tokenno": min(no,9) })
        self.TokensFrom = where
        if no > 0:
            musicsound.PlaySound("tokens.pick")
        
    def _DropTokensTo(self, where):
        if where != None:
            where.DropTokens()
        gamegui.SetCursorState({"state": "Empty"})
        self.TokensFrom = None
        
    def _UpdateLevelInfo(self):
        self.Expert = (self.LevelScore >= globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("moneyGoal"))
        gamegui.UpdateGameHUD({ "RemainingCustomers": self.RemainingCustomers,
                               "LevelScore": self.LevelScore,
                               "Expert": self.Expert })
        
    #--------------------------
    # очистка игрового поля
    #--------------------------
    def Clear(self):
        try:
            oE.executor.GetQueue(self.QueNo).Suspend()
            self.Playing = False
            for tmp in self.CStations + self.TrashCans: 
                tmp.Kill()
            self.CStations = []
            self.TrashCans = []
            
            for tmp in self.Stores+self.Fields+self.Conveyors:
                tmp.Clear()
                del tmp
            self.Stores = []
            self.Fields = []
            self.Conveyors = []
                
            for spr in self.Static:
                spr.Dispose()
            self.Static = []
            
            if self.CustomersQue != None:
                self.CustomersQue.Kill()
                self.CustomersQue = None
            if self.Advisor != None:
                self.Advisor.Kill()
                self.Advisor = None
        except:
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
             
    def Show(self, flag):
        """
        Показать - спрятать
        """    
        self.BgSprite.visible = flag
        self.DoorSprite.visible = flag
        self.BgReceptor.visible = flag
        #if self.Playing:
        #    self.CustomersQue.Show(flag)
        #    for tmp in self.CStations:
        #        tmp.Show(flag)
        
    def Freeze(self, flag, fullFreeze = True):
        """
        Постановка паузы
        """
        self.Frozen = flag
        if flag:
            #oE.executor.GetQueue(self.QueNo).Suspend()
            if fullFreeze:
                oE.executor.GetQueue(self.QueNo).Suspend()
                self.SendCommand(Cmd_DropWhatYouCarry)
        else:
            oE.executor.GetQueue(self.QueNo).Resume()
        if self.Playing:
            self.Advisor.Freeze(flag)
            self.CustomersQue.Freeze(flag)
            for tmp in self.Stores+self.Fields+self.Conveyors:
                tmp.Freeze(flag, fullFreeze)
            for tmp in self.CStations:
                tmp.Freeze(flag)
        
def _ListIntersection(list1, list2):
    return filter(lambda x: x in list2, list1)

