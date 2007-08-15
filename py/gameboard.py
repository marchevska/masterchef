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
from guielements import *
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

class GameBoard(scraft.Dispatcher):
    
    def __init__(self):
        self.BgSprite = MakeSimpleSprite("$spritecraft$dummy$", Layer_GameBg, 0, 0)
        self.DoorSprite = MakeSimpleSprite("$spritecraft$dummy$", Layer_Door, Crd_DoorX, Crd_DoorY)
        self.BgReceptor = MakeDummySprite(self, Cmd_BgReceptor,
                        400, 300, 800, 600, Layer_BgReceptor)
        
        #create text sprites
        self.HudElements = {}
        self.HudElements["InfoPane"] = MakeSprite("$spritecraft$dummy$", Layer_InterfaceBg, { "x": 1, "y": 0 })
        self.HudElements["LevelText"] = MakeSprite(u"simple", Layer_InterfaceTxt,
                                    {"x": 77, "y": 18, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_LevelText, "cfilt-color": 0x604020})
        self.HudElements["ScoreText"] = MakeSprite(u"simple", Layer_InterfaceTxt,
                                    {"x": 150, "y": 18, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_ScoreText, "cfilt-color": 0x604020})
        self.HudElements["GoalText"] = MakeSprite(u"simple", Layer_InterfaceTxt,
                                    {"x": 235, "y": 18, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_GoalText, "cfilt-color": 0x604020})
        self.HudElements["NoPeopleText"] = MakeSprite(u"simple", Layer_InterfaceTxt,
                                    {"x": 298, "y": 18, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_NoPeopleText, "cfilt-color": 0x604020})
        self.HudElements["LevelName"] = MakeSprite(u"domcasual-11", Layer_InterfaceTxt,
                                    {"x": 77, "y": 37, "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0xC04020})
        self.HudElements["Score"] = MakeSprite(u"domcasual-20-green", Layer_InterfaceTxt,
                                    {"x": 150, "y": 40, "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0xFFFFF})
        self.HudElements["Goal"] = MakeSprite(u"domcasual-11", Layer_InterfaceTxt,
                                    {"x": 235, "y": 37, "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0xC04020})
        self.HudElements["NoPeople"] = MakeSprite(u"domcasual-11", Layer_InterfaceTxt,
                                    {"x": Crd_QueueMarker_TextX, "y": Crd_QueueMarker_TextY,
                                     "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0xC04020})
        
        #create buttons
        self.GameButtons = {}
        self.GameButtons["Menu"] = PushButton("Menu",
                self, Cmd_Menu, PState_Game,
                "$spritecraft$dummy$", [0, 1, 2, 3, 4], 
                Layer_InterfaceBtn, 28, 31, 40, 40)
        
        self.CustomersQue = None
        self.Fields = []
        self.TrashCans = []
        self.CStations = []
        self.Stores = []
        self.Conveyors = []
        self.Static = []
        self.TokenSprite = None
        self.TokensNoSprite = None
        self.ToolSprite = None
        self.TokensFrom = None
        self.NoErrors = 0
        
        self.Playing = False
        self.MyRand = oE.NewRandomizer()
        self._SetState(GameState_None)
        globalvars.BlackBoard.Update(BBTag_Cursor, {"state": GameCursorState_Default})
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
        except:
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        self._StartLevel()
        
    def _StartLevel(self):
        self.Expert = False
        self.HudElements["LevelName"].text = self.LevelName
        self.HudElements["GoalText"].text = Str_HUD_GoalText
        self.HudElements["Goal"].text = str(globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("moneygoal"))
        self.HudElements["NoPeople"].text = str(self.RemainingCustomers)
        self._UpdateLevelInfo()
        
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
        self.LevelName = globalvars.CurrentPlayer.GetLevel().GetStrAttr(u"name")
        
        tmpTheme = globalvars.ThemesInfo.GetSubtag(globalvars.LevelSettings.GetTag("Layout").GetStrAttr(u"theme"))
        self.BgSprite.ChangeKlassTo(tmpTheme.GetStrAttr("background"))
        self.DoorSprite.ChangeKlassTo("$spritecraft$dummy$")
        self.HudElements["InfoPane"].ChangeKlassTo(tmpTheme.GetStrAttr("infopane"))
        self.GameButtons["Menu"].SetButtonKlass(tmpTheme.GetStrAttr("menuButton"))
        
        #reset customer dispatcher
        self.RemainingCustomers = globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("noCustomers")
        tmp = globalvars.LevelSettings.GetTag("Layout").GetTag("CustomersQue")
        self.CustomersQue = CustomersQue(tmpTheme, tmp.GetIntAttr("X"), tmp.GetIntAttr("Y"))
        
        #размещение стейшенов 
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("CustomerStation"):
            tmpStation = CustomerStation(tmp.GetIntAttr("x"), tmp.GetIntAttr("y"), tmpTheme)
            if tmp.GetBoolAttr("occupied"):
                self._NextCustomerTo(tmpStation)
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
            self.Static.append(MakeSimpleSprite(tmpTheme.GetStrAttr("counter"), Layer_Counter,
                globalvars.LevelSettings.GetTag("Layout").GetTag("Counter").GetIntAttr("x"),
                globalvars.LevelSettings.GetTag("Layout").GetTag("Counter").GetIntAttr("y")))
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("Decoration"):
            self.Static.append(MakeSimpleSprite(tmp.GetStrAttr("type"), Layer_Deco, tmp.GetIntAttr("x"), tmp.GetIntAttr("y")))
        
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
        
        self._SetState(GameState_StartLevel)
        #globalvars.BlackBoard.Update(BBTag_Cursor, {"state": GameCursorState_Default})
        #globalvars.BlackBoard.Update(BBTag_Cursor, {"button": ButtonState_Up})
        
    #--------------------------
    # Поместить следующего покупателя к заданному стейшену
    #--------------------------
    def _NextCustomerTo(self, station):
        station.SetState(CStationState_Busy)
        station.AttachCustomer(self.CustomersQue.PopCustomer())
        self.RemainingCustomers -= 1
        self.HudElements["NoPeople"].text = str(self.RemainingCustomers)
        if self.RemainingCustomers <= 0:
            tmpTheme = globalvars.ThemesInfo.GetSubtag(globalvars.LevelSettings.GetTag("Layout").GetStrAttr(u"theme"))
            self.DoorSprite.ChangeKlassTo(tmpTheme.GetStrAttr("door"))
            tmp = globalvars.LevelSettings.GetTag("Layout").GetTag("Door")
        
    #--------------------------
    # обработка входящих команд
    #--------------------------
    def SendCommand(self, cmd, parameter = None):
        if cmd == Cmd_Menu:
            globalvars.GUI.CallInternalMenu() 
            globalvars.Musician.PlaySound("gui.click")
            
        if cmd == Cmd_MovementFinished:
            if self.State == GameState_StartLevel:
                self._SetState(GameState_Play)
            
        #переполнение коллапсоида - штраф и удаление лишнего
        elif cmd == Cmd_CollapsoidFull:
            tmp = parameter.GetBurnCrd()
            parameter.SendCommand(Cmd_CollapsoidBurn)
            #максимальный штраф задан (=10 или около того)
            self.NoErrors = min(self.NoErrors+1, globalvars.GameSettings.GetIntAttr("maxColapsoidErrors"))
            self.AddScore(-self.NoErrors*len(tmp))
            for (x, y) in tmp:
                PopupText(str(-self.NoErrors), "domcasual-20-red", x, y,
                                InPlaceMotion(), BlinkTransp(400, 0.4, -50), BlinkScale(-100, 0.4, 150), 1500)
            
        elif cmd == Cmd_ClickStation:
            if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tokens:
                if parameter["hasOrder"] and not parameter["mealReady"]:
                    if parameter["station"].CanAddTokens():
                        tmpFrom = self.TokensFrom
                        tmpDeltaScore = parameter["station"].AddTokens()
                        self.AddScore(tmpDeltaScore)
                        if tmpDeltaScore > 0:
                            globalvars.Musician.PlaySound("tokens.give")
                        PopupText("+"+str(tmpDeltaScore), "domcasual-20-green",
                                        parameter["station"].CrdX, parameter["station"].CrdY,
                                        BubbleMotion(16, -100), FadeAwayTransp(50, -25))
                        if tmpFrom.Collapsing:
                            tmpX, tmpY = tmpFrom.GetCentralCrd()
                            if globalvars.BlackBoard.Inspect(BBTag_Cursor)["tokenno"] > globalvars.GameSettings.GetIntAttr("tokenForIncreadible"):
                                PopupText(Str_Incredible, "domcasual-20-yellow", tmpX, tmpY,
                                    InPlaceMotion(), BlinkTransp(400, 0.4, -50),
                                    BounceScale([(0, 50), (0.3, 100), (0.8, 110), (1.2, 140), (1.5, 200)]), 1500)
                            elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["tokenno"] > globalvars.GameSettings.GetIntAttr("tokensForGreat"):
                                PopupText(Str_Great, "domcasual-20-yellow", tmpX, tmpY,
                                    InPlaceMotion(), BlinkTransp(400, 0.4, -50),
                                    BounceScale([(0, 50), (0.3, 100), (0.8, 110), (1.2, 140), (1.5, 200)]), 1500)
                        self.TokensFrom.RemoveTokens()
                        self.SendCommand(Cmd_DropWhatYouCarry)
                        if tmpFrom in self.Fields:
                            tmpFrom.SetState(FieldState_Collapse)
                    
            #иначе - использовать бонус
            elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tool:
                if globalvars.BlackBoard.Inspect(BBTag_Cursor)["tooltype"] in ('bonus.sweet', 'bonus.gift'):
                    if globalvars.BlackBoard.Inspect(BBTag_Cursor)["tooltype"] == 'bonus.sweet':
                        globalvars.Musician.PlaySound("customer.gotgift")
                        parameter["station"].Customer.GiveSweet()
                    elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["tooltype"] == 'bonus.gift':
                        globalvars.Musician.PlaySound("customer.gotgift")
                        parameter["station"].Customer.GiveGift()
                    tmpFrom = self.TokensFrom
                    self.TokensFrom.RemoveTokens()
                    self.SendCommand(Cmd_DropWhatYouCarry)
                    if tmpFrom in self.Fields:
                        tmpFrom.SetState(FieldState_Collapse)
                
        elif cmd == Cmd_ClickStorage:
            if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tokens:
                if parameter["where"].HasFreeSlots(globalvars.BlackBoard.Inspect(BBTag_Cursor)["tokenno"]):# and self.TokensFrom == self:
                    tmpFrom = self.TokensFrom
                    tmpType = globalvars.BlackBoard.Inspect(BBTag_Cursor)["tokentype"]
                    tmpNo = globalvars.BlackBoard.Inspect(BBTag_Cursor)["tokenno"]
                    tmpFrom.RemoveTokens()
                    self.SendCommand(Cmd_DropWhatYouCarry)
                    parameter["where"].AddTokens(tmpType, tmpNo, parameter["pos"])
                    if tmpFrom in self.Fields:
                        tmpFrom.SetState(FieldState_Collapse)
            
        elif cmd == Cmd_TrashCan:
            if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tokens:
                tmpFrom = self.TokensFrom
                tmpNo = globalvars.BlackBoard.Inspect(BBTag_Cursor)["tokenno"]
                self.TokensFrom.RemoveTokens()
                self._DropTokensTo(tmpFrom)
                parameter.Discard(tmpNo)
                if tmpFrom in self.Fields:
                    tmpFrom.SetState(FieldState_Collapse)
            
        elif cmd == Cmd_DropWhatYouCarry:
            if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tokens:
                if self.TokensFrom != None:
                    self._DropTokensTo(self.TokensFrom)
            elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tool:
                if self.TokensFrom != None:
                    self._DropPowerUp(self.TokensFrom)
                else:
                    self._DropTool()
            globalvars.BlackBoard.Update(BBTag_Cursor, {"state": GameCursorState_Default,
                                                "tokentype": "", "tokenno": 0})
            
        elif cmd == Cmd_PickFromStorage:
            self._PickTokensFrom(parameter["where"], parameter["type"], parameter["no"])
            
        elif cmd == Cmd_PickFromConveyor:
            if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tokens:
                if self.TokensFrom != None:
                    parameter["where"].SendCommand(Cmd_ReturnToConveyor,
                                    { "type": globalvars.BlackBoard.Inspect(BBTag_Cursor)["tokentype"],
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
            if parameter["amount"] > 0:
                if parameter.has_key("tips"):
                    self.AddScore(parameter["tips"])
                    PopupText("+$"+str(parameter["amount"])+"+$"+str(parameter["tips"]), "domcasual-20-orange",
                            parameter["station"].CrdX-20, parameter["station"].CrdY-20,
                            BubbleMotion(16, -100), FadeAwayTransp(50, -25))
                else:
                    PopupText("+$"+str(parameter["amount"]), "domcasual-20-green",
                            parameter["station"].CrdX, parameter["station"].CrdY,
                            BubbleMotion(16, -100), FadeAwayTransp(50, -25))
            elif parameter["amount"] < 0:
                PopupText("-$"+str(-parameter["amount"]), "domcasual-20-red",
                            parameter["station"].CrdX, parameter["station"].CrdY,
                            BubbleMotion(16, -100), FadeAwayTransp(50, -25))
            
        elif cmd == Cmd_PickPowerUp:
            self._PickPowerUp(parameter["type"], parameter["where"])
        
        elif cmd == Cmd_UtilizePowerUp:
            if parameter == 'bonus.hearts':
                for tmp in self.CStations:
                    if tmp.Active:
                        tmp.Customer.GiveSweet()
                        
        #экстренное завершение уровня в отладочном режиме
        elif cmd == Cmd_DebugFinishLevel:       
            self.LevelScore = max(self.LevelScore,
                globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("moneygoal"))
            self._SetState(GameState_EndLevel)
            
        elif cmd == Cmd_DebugLoseLevel:       
            self._SetState(GameState_EndLevel)
            
        elif cmd == Cmd_DebugLastCustomer:
            if self.RemainingCustomers > 1:
                self.RemainingCustomers = 1 
            
    def AddScore(self, delta):
        self.LevelScore = max(self.LevelScore + delta, 0)
        self._UpdateLevelInfo()
        if self.LevelScore >= globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("moneygoal") and not self.Expert:
            self._SwitchToExpert()
    
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
                globalvars.GUI.CallLevelCompleteDialog(False,
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
                globalvars.GUI.CallLevelCompleteDialog((self.LevelScore >= globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("moneygoal")),
                        { "served": self.CustomersServed, "lost": self.CustomersLost, "score": self.LevelScore,
                         "expert": self.LevelScore >= globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("expertgoal") } )
                print "level", self.LevelName, "time", (oE.millis-self.StartTime)/1000
        
        
    #--------------------------
    # основной цикл
    #--------------------------
    def _OnExecute(self, que) :
        try:
            if self.State == GameState_StartLevel:
                pass
                
            elif self.State == GameState_Play:
                #перенос токенов или иконки бонуса на мыши
                if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tokens:
                    self.TokenSprite.x = oE.mouseX + Crd_TokenSpriteDx
                    self.TokenSprite.y = oE.mouseY + Crd_TokenSpriteDy
                elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tool:
                    self.ToolSprite.x = oE.mouseX + Crd_ToolSpriteDx
                    self.ToolSprite.y = oE.mouseY + Crd_ToolSpriteDy
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
        self.ToolSprite = MakeSprite(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(type).GetStrAttr("src"), Layer_Tools)
        globalvars.BlackBoard.Update(BBTag_Cursor, {"state": GameCursorState_Tool, "tooltype": type})
        self.TokensFrom = where
    
    #--------------------------
    # Сбрасывает иконку бонуса (тулза)
    #--------------------------
    def _DropPowerUp(self, where):
        if where != None:
            where.DropTokens()
        self.ToolSprite.Dispose()
        self.ToolSprite = None
        globalvars.BlackBoard.Update(BBTag_Cursor, {"state": GameCursorState_Default, "tooltype": ""})
        self.TokensFrom = None
        
    def _PickFromConveyor(self, where, type):
        self.TokenSprite = MakeSprite(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(type).GetStrAttr("iconSrc"), Layer_Tools)
        self.TokensNoSprite = MakeSprite("domcasual-11", Layer_Tools-1,
                                        { "parent": self.TokenSprite, "x": Crd_TokenNoSpriteDx,
                                         "y": Crd_TokenNoSpriteDy, "text": "",
                                          "hotspot": scraft.HotspotCenter, "cfilt-color": 0x000000 })
        globalvars.BlackBoard.Update(BBTag_Cursor, {"state": GameCursorState_Tokens,
                                                "tokentype": type, "tokenno": 1 })
        self.TokensFrom = where
        globalvars.Musician.PlaySound("tokens.pick")
        
        
    def _PickTokensFrom(self, where, type, no):
        self.TokenSprite = MakeSprite(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(type).GetStrAttr("iconSrc"), Layer_Tools)
        self.TokensNoSprite = MakeSprite("domcasual-11", Layer_Tools-1,
                                        { "parent": self.TokenSprite, "x": Crd_TokenNoSpriteDx,
                                         "y": Crd_TokenNoSpriteDy, "text": str(min(no,9)),
                                          "hotspot": scraft.HotspotCenter, "cfilt-color": 0x000000 })
        globalvars.BlackBoard.Update(BBTag_Cursor, {"state": GameCursorState_Tokens,
                                                "tokentype": type, "tokenno": no })
        self.TokensFrom = where
        if no > 0:
            globalvars.Musician.PlaySound("tokens.pick")
        
    def _DropTokensTo(self, where):
        if where != None:
            where.DropTokens()
        self.TokenSprite.Dispose()
        self.TokensNoSprite.Dispose()
        globalvars.BlackBoard.Update(BBTag_Cursor, {"state": GameCursorState_Default,
                                                "tokentype": "", "tokenno": 0})
        self.TokensFrom = None
        
    def _UpdateLevelInfo(self):
        self.HudElements["Score"].text = str(self.LevelScore)
        
    def _SwitchToExpert(self):
        self.HudElements["GoalText"].text = Str_HUD_ExpertText
        self.HudElements["Goal"].text = str(globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("expertgoal"))
        self.Expert = True
        
    #--------------------------
    # очистка игрового поля
    #--------------------------
    def Clear(self):
        try:
            oE.executor.GetQueue(self.QueNo).Suspend()
            self.Playing = False
            if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tokens:
                self.TokenSprite.Dispose()
                self.TokensNoSprite.Dispose()
            elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tool:
                self.ToolSprite.Dispose()
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
        except:
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
             
    def Show(self, flag):
        """
        Показать - спрятать
        """    
        self.BgSprite.visible = flag
        self.DoorSprite.visible = flag
        self.BgReceptor.visible = flag
        for spr in self.HudElements.values():
            spr.visible = flag
        for btn in self.GameButtons.values():
            btn.Show(flag)
        #if self.Playing:
        #    self.CustomersQue.Show(flag)
        #    for tmp in self.CStations:
        #        tmp.Show(flag)
        
    def Freeze(self, flag):
        """
        Постановка паузы
        """
        if flag:
            self.SendCommand(Cmd_DropWhatYouCarry)
            oE.executor.GetQueue(self.QueNo).Suspend()
        else:
            oE.executor.GetQueue(self.QueNo).Resume()
        if self.Playing:
            self.CustomersQue.Freeze(flag)
            for tmp in self.Stores+self.Fields+self.Conveyors:
                tmp.Freeze(flag)
            for tmp in self.CStations:
                tmp.Freeze(flag)
        
def _ListIntersection(list1, list2):
    return filter(lambda x: x in list2, list1)

