#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef 
Игровое поле
"""

import sys
import string
from random import choice, shuffle
import scraft
from scraft import engine as oE
from constants import *
from configconst import *
from guielements import *
from customerstation import CustomerStation
from storage import Store, SingularStore, Field, TrashCan, Collapsoid
from conveyor import Conveyor
from extra import *
from customer import *
import config
import defs
import playerlist
import globalvars
import traceback

class GameBoard(scraft.Dispatcher):
    
    def __init__(self):
        self.BgSprite = MakeSimpleSprite(u"$spritecraft$dummy$", Layer_GameBg, 0, 0)
        self.BgReceptor = MakeDummySprite(self, Cmd_BgReceptor,
                        400, 300, 800, 600, Layer_BgReceptor)
        
        #create text sprites
        self.HudElements = {}
        self.HudElements["InfoPane"] = MakeSimpleSprite(u"info-pane", Layer_InterfaceBg, 275, 40)
        self.HudElements["LevelText"] = MakeSprite(u"domcasual-10", Layer_InterfaceTxt,
                                    {"x": 185, "y": 31, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_LevelText, "cfilt-color": 0x604020})
        self.HudElements["ScoreText"] = MakeSprite(u"domcasual-10", Layer_InterfaceTxt,
                                    {"x": 237, "y": 31, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_ScoreText, "cfilt-color": 0x604020})
        self.HudElements["GoalText"] = MakeSprite(u"domcasual-10", Layer_InterfaceTxt,
                                    {"x": 293, "y": 31, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_GoalText, "cfilt-color": 0x604020})
        self.HudElements["LevelName"] = MakeSprite(u"domcasual-11", Layer_InterfaceTxt,
                                    {"x": 185, "y": 51, "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0xC04020})
        self.HudElements["Score"] = MakeSprite(u"hobor-17", Layer_InterfaceTxt,
                                    {"x": 237, "y": 50, "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0xFF8000})
        self.HudElements["Goal"] = MakeSprite(u"domcasual-11", Layer_InterfaceTxt,
                                    {"x": 293, "y": 51, "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0xC04020})
        
        #create buttons
        self.GameButtons = {}
        self.GameButtons["Menu"] = PushButton("Menu",
                self, Cmd_Menu, PState_Game,
                u"button-4st", [0, 1, 2, 3, 4], 
                Layer_InterfaceBtn, 60, 25, 100, 34,
                Str_HUD_MenuButton, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        
        self.CustomersQue = None
        self.Fields = []
        self.TrashCans = []
        self.CStations = []
        self.Stores = []
        self.Conveyors = []
        self.Static = []
        self.PickedTool = ""
        self.PickedTokens = ""
        self.PickedTokensNo = 0
        self.TokenSprite = None
        self.TokensNoSprite = None
        self.ToolSprite = None
        self.TokensFrom = None
        self.NoErrors = 0
        
        self.Playing = False
        self.MyRand = oE.NewRandomizer()
        self._SetState(GameState_None)
        self._SetGameCursorState(GameCursorState_Default)
        self.QueNo = oE.executor.Schedule(self)
        self.Show(False)
        self.Freeze(True)
        
    def LaunchLevel(self):
        self.Freeze(False)
        try:
            self.Load()
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        self._StartLevel()
        #self.SaveGame()
        
    def _StartLevel(self):
        self.Expert = False
        self.HudElements["LevelName"].text = unicode(self.LevelName)
        self.HudElements["GoalText"].text = unicode(Str_HUD_GoalText)
        self.HudElements["Goal"].text = unicode(str(globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("moneygoal")))
        self._UpdateLevelInfo()
        
    def Restart(self):
        self.Clear()
        self.LaunchLevel()
        
    def _EndLevel(self, flag):
        """ Завершение уровня
            flag == True означает победу в уровне
            flag == False - поражение (игрок не уложился по времени)
        """
        pass
        
    def _EndGame(self, flag):
        """ Завершение игры
            flag == True означает полное прохождение игры
            flag == False - поражение (жизни закончились)
        """
        pass
        
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
        
        #reset customer dispatcher
        self.RemainingCustomers = globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("noCustomers")
        self.CustomersQue = CustomersQue(tmpTheme)
        
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
                        tmp.GetIntAttr("InitialRows"), tmp.GetIntAttr("Delay"), tmp.GetIntAttr("DropIn"),
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
        self._SetGameCursorState(GameCursorState_Default)
        
    #--------------------------
    # Поместить следующего покупателя к заданному стейшену
    #--------------------------
    def _NextCustomerTo(self, station):
        station.SetState(CStationState_Busy)
        station.AttachCustomer(self.CustomersQue.PopCustomer())
        self.RemainingCustomers -= 1
        
    #--------------------------
    # обработка входящих команд
    #--------------------------
    def SendCommand(self, cmd, parameter = None):
        if cmd == Cmd_Menu:
            globalvars.GUI.CallInternalMenu() 
            oE.PlaySound(u"click", Channel_Default)
            
        if cmd == Cmd_MovementFinished:
            if self.State == GameState_StartLevel:
                self._SetState(GameState_Play)
            
        #переполнение коллапсоида - штраф и сжигание лишнего
        elif cmd == Cmd_CollapsoidFull:
            tmp = parameter.GetBurnCrd()
            parameter.SendCommand(Cmd_CollapsoidBurn)
            #максимальный штраф задан (=10 или около того)
            self.NoErrors = min(self.NoErrors+1, globalvars.GameSettings.GetIntAttr("maxColapsoidErrors"))
            self.AddScore(-self.NoErrors*len(tmp))
            for (x, y) in tmp:
                self._PopupText(str(-self.NoErrors), "hobor-17", x, y)
            
        elif cmd == Cmd_ClickStation:
            if self.GameCursorState == GameCursorState_Tokens:
                if parameter["hasOrder"] and not parameter["mealReady"]:
                    if parameter["station"].CanAddTokens(self.PickedTokens, self.PickedTokensNo):
                        tmpFrom = self.TokensFrom
                        tmpDeltaScore = parameter["station"].AddTokens(self.PickedTokens, self.PickedTokensNo)
                        self.AddScore(tmpDeltaScore)
                        self._PopupText(str(tmpDeltaScore), "hobor-17", parameter["station"].CrdX, parameter["station"].CrdY)
                        self.TokensFrom.RemoveTokens()
                        self.SendCommand(Cmd_DropWhatYouCarry)
                        if tmpFrom in self.Fields:
                            tmpFrom.SetState(FieldState_Collapse)
                    
            #иначе - использовать бонус
            elif self.GameCursorState == GameCursorState_Tool:
                if self.PickedTool in ('bonus.sweet', 'bonus.gift'):
                    if self.PickedTool == 'bonus.sweet':
                        parameter["station"].Customer.GiveSweet()
                    elif self.PickedTool == 'bonus.gift':
                        parameter["station"].Customer.GiveGift()
                    tmpFrom = self.TokensFrom
                    self.TokensFrom.RemoveTokens()
                    self.SendCommand(Cmd_DropWhatYouCarry)
                    if tmpFrom in self.Fields:
                        tmpFrom.SetState(FieldState_Collapse)
                
        elif cmd == Cmd_ClickStorage:
            if self.GameCursorState == GameCursorState_Tokens:
                if parameter["where"].HasFreeSlots(self.PickedTokensNo):# and self.TokensFrom == self:
                    tmpFrom = self.TokensFrom
                    tmpType = self.PickedTokens
                    tmpNo = self.PickedTokensNo
                    tmpFrom.RemoveTokens()
                    self.SendCommand(Cmd_DropWhatYouCarry)
                    parameter["where"].AddTokens(tmpType, tmpNo, parameter["pos"])
                    if tmpFrom in self.Fields:
                        tmpFrom.SetState(FieldState_Collapse)
            
        elif cmd == Cmd_TrashCan:
            if self.GameCursorState == GameCursorState_Tokens:
                tmpFrom = self.TokensFrom
                tmpNo = self.PickedTokensNo
                self.TokensFrom.RemoveTokens()
                self._DropTokensTo(tmpFrom)
                parameter.Discard(tmpNo)
                if tmpFrom in self.Fields:
                    tmpFrom.SetState(FieldState_Collapse)
            
        elif cmd == Cmd_DropWhatYouCarry:
            if self.GameCursorState == GameCursorState_Tokens:
                if self.TokensFrom != None:
                    self._DropTokensTo(self.TokensFrom)
            elif self.GameCursorState == GameCursorState_Tool:
                if self.TokensFrom != None:
                    self._DropPowerUp(self.TokensFrom)
                else:
                    self._DropTool()
            
        elif cmd == Cmd_PickFromStorage:
            self._PickTokensFrom(parameter["where"], parameter["type"], parameter["no"])
            
        elif cmd == Cmd_PickFromConveyor:
            if self.GameCursorState == GameCursorState_Tokens:
                if self.TokensFrom != None:
                    parameter["where"].SendCommand(Cmd_ReturnToConveyor,
                                    { "type": self.PickedTokens, "position": parameter["position"] })
            self._PickFromConveyor(parameter["where"], parameter["type"])
            
        elif cmd == Cmd_NewCustomer:
            tmpFreeStations = filter(lambda x: x.State == CStationState_Free, self.CStations)
            self._NextCustomerTo(choice(tmpFreeStations))
            if self.RemainingCustomers > 0 and len(tmpFreeStations) > 1:
                self.CustomersQue.SetState(QueState_Active)
                
        elif cmd == Cmd_CustomerServed:
            self.CustomersServed += 1
            
        elif cmd == Cmd_CustomerLost:
            self.CustomersLost += 1
                
        elif cmd == Cmd_FreeStation:
            if self.RemainingCustomers > 0:
                self.CustomersQue.SetState(QueState_Active)
                
        elif cmd == Cmd_PickPowerUp:
            self._PickPowerUp(parameter["type"], parameter["where"])
        
        elif cmd == Cmd_UtilizePowerUp:
            if parameter == 'bonus.hearts':
                for tmp in self.CStations:
                    tmp.Customer.GiveSweet()
            
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
            for tmp in self.Fields:
               tmp.SetState(FieldState_StartLevel)
            self._SetState(GameState_Play)
            pass
            
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
        
        
    #--------------------------
    # основной цикл
    #--------------------------
    def _OnExecute(self, que) :
        try:
            if self.State == GameState_StartLevel:
                pass
                
            elif self.State == GameState_Play:
                #перенос токенов или иконки бонуса на мыши
                if self.GameCursorState == GameCursorState_Tokens:
                    self.TokenSprite.x = oE.mouseX
                    self.TokenSprite.y = oE.mouseY
                elif self.GameCursorState == GameCursorState_Tool:
                    self.ToolSprite.x = oE.mouseX
                    self.ToolSprite.y = oE.mouseY
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
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        return scraft.CommandStateRepeat
        
    #--------------------------
    # Задает состояние игрового курсора (свободный, держит токены, держит тул)
    #--------------------------
    def _SetGameCursorState(self, state):
        self.GameCursorState = state
        
    #--------------------------
    # Подбирает иконку бонуса
    #--------------------------
    def _PickPowerUp(self, type, where):
        self.SendCommand(Cmd_DropWhatYouCarry)
        self.ToolSprite = MakeSprite(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(type).GetStrAttr("src"), Layer_Tools)
        self.PickedTool = type
        self._SetGameCursorState(GameCursorState_Tool)
        self.TokensFrom = where
    
    #--------------------------
    # Сбрасывает иконку бонуса (тулза)
    #--------------------------
    def _DropPowerUp(self, where):
        if where != None:
            where.DropTokens()
        self.ToolSprite.Dispose()
        self.ToolSprite = None
        self.PickedTool = ""
        self._SetGameCursorState(GameCursorState_Default)
        self.TokensFrom = None
        
    def _PickFromConveyor(self, where, type):
        self.PickedTokens = type
        self.PickedTokensNo = 1
        self.TokenSprite = MakeSprite(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(type).GetStrAttr("src"), Layer_Tools)
        self.TokensNoSprite = MakeSprite("domcasual-11", Layer_Tools-1,
                                        { "parent": self.TokenSprite, "x": 20, "y": 30, "text": "",
                                          "hotspot": scraft.HotspotCenter, "cfilt-color": 0x000000 })
        self._SetGameCursorState(GameCursorState_Tokens)
        self.TokensFrom = where
        
        
    def _PickTokensFrom(self, where, type, no):
        self.PickedTokens = type
        self.PickedTokensNo = no
        self.TokenSprite = MakeSprite(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(type).GetStrAttr("src"), Layer_Tools)
        self.TokensNoSprite = MakeSprite("domcasual-11", Layer_Tools-1,
                                        { "parent": self.TokenSprite, "x": 20, "y": 30, "text": str(no),
                                          "hotspot": scraft.HotspotCenter, "cfilt-color": 0x000000 })
        self._SetGameCursorState(GameCursorState_Tokens)
        self.TokensFrom = where
        
    def _DropTokensTo(self, where):
        if where != None:
            where.DropTokens()
        self.PickedTokens = ""
        self.PickedTokensNo = 0
        self.TokenSprite.Dispose()
        self.TokensNoSprite.Dispose()
        self._SetGameCursorState(GameCursorState_Default)
        self.TokensFrom = None
        
    def _PopupText(self, text, font, x, y):
        spr = MakeTextSprite(font, Layer_Popups, x, y, scraft.HotspotCenter, text)
        spr.cfilt.color = 0xFF8000
        tmp = Popup(spr, "Bubble", "FadeOut")
        
    def _UpdateLevelInfo(self):
        self.HudElements["Score"].text = unicode(str(self.LevelScore))
        
    def _SwitchToExpert(self):
        self.HudElements["GoalText"].text = unicode(Str_HUD_ExpertText)
        self.HudElements["Goal"].text = unicode(str(globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("expertgoal")))
        self.Expert = True
        
    #--------------------------
    # очистка игрового поля
    #--------------------------
    def Clear(self):
        oE.executor.GetQueue(self.QueNo).Suspend()
        self.Playing = False
        if self.GameCursorState == GameCursorState_Tokens:
            self.TokenSprite.Dispose()
            self.TokensNoSprite.Dispose()
        elif self.GameCursorState == GameCursorState_Tool:
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
        
        self.CustomersQue.Kill()
        self.CustomersQue = None
             
    def Show(self, flag):
        """
        Показать - спрятать
        """    
        self.BgSprite.visible = flag
        self.BgReceptor.visible = flag
        for spr in self.HudElements.values():
            spr.visible = flag
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

