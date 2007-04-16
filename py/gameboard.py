#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef 
������� ����
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
from storage import Store, SingularStore, Field, TrashCan
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
        self.HudElements["InfoPane"] = MakeSimpleSprite(u"info-pane", Layer_InterfaceBg, 675, 40)
        self.HudElements["LevelText"] = MakeSprite(u"domcasual-10", Layer_InterfaceTxt,
                                    {"x": 585, "y": 31, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_LevelText, "cfilt-color": 0x604020})
        self.HudElements["ScoreText"] = MakeSprite(u"domcasual-10", Layer_InterfaceTxt,
                                    {"x": 637, "y": 31, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_ScoreText, "cfilt-color": 0x604020})
        self.HudElements["GoalText"] = MakeSprite(u"domcasual-10", Layer_InterfaceTxt,
                                    {"x": 693, "y": 31, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_GoalText, "cfilt-color": 0x604020})
        self.HudElements["ApprovalText"] = MakeSprite(u"domcasual-10", Layer_InterfaceTxt,
                                    {"x": 750, "y": 31, "hotspot": scraft.HotspotCenter,
                                     "text": Str_HUD_ApprovalText, "cfilt-color": 0x604020})
        self.HudElements["LevelName"] = MakeSprite(u"domcasual-11", Layer_InterfaceTxt,
                                    {"x": 585, "y": 51, "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0xC04020})
        self.HudElements["Score"] = MakeSprite(u"hobor-17", Layer_InterfaceTxt,
                                    {"x": 637, "y": 50, "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0xFF8000})
        self.HudElements["Goal"] = MakeSprite(u"domcasual-11", Layer_InterfaceTxt,
                                    {"x": 693, "y": 51, "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0xC04020})
        self.HudElements["Approval"] = MakeSprite(u"powerups", Layer_InterfaceTxt,
                                    {"x": 750, "y": 51, "hotspot": scraft.HotspotCenter,
                                     "cfilt-color": 0x604020})
        
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
        self.PowerUpButtons = {}
        self.BuyPowerUpButtons = {}
        self.HasPowerUps = {}
        self.TokensFrom = None
        
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
        """ ���������� ������
            flag == True �������� ������ � ������
            flag == False - ��������� (����� �� �������� �� �������)
        """
        pass
        
    def _EndGame(self, flag):
        """ ���������� ����
            flag == True �������� ������ ����������� ����
            flag == False - ��������� (����� �����������)
        """
        pass
        
    #--------------------------
    # �������� ������
    #--------------------------
    def Load(self):
        
        self.Playing = True
        defs.ReadLevelSettings(globalvars.CurrentPlayer.GetLevel().GetContent())
        
        self.LevelScore = 0
        self.Approval = 0
        self.CustomersServed = 0
        self.CustomersLost = 0
        self.LevelName = globalvars.CurrentPlayer.GetLevel().GetStrAttr(u"name")
        
        self.HasPowerUps = {}
        
        tmpTheme = globalvars.ThemesInfo[globalvars.LevelSettings.GetTag("Layout").GetStrAttr(u"theme")]
        self.BgSprite.ChangeKlassTo(unicode(tmpTheme["background"]))
        
        #reset customer dispatcher
        self.RemainingCustomers = globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("noCustomers")
        self.CustomersQue = CustomersQue(tmpTheme)
        
        #���������� ��������� 
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("CustomerStation"):
            tmpStation = CustomerStation(tmp.GetIntAttr("x"), tmp.GetIntAttr("y"), tmpTheme)
            if tmp.GetBoolAttr("occupied"):
                self._NextCustomerTo(tmpStation)
            else:
                tmpStation.SetState(CStationState_Free)
            self.CStations.append(tmpStation)
        
        #������� ����, ���������� �������
        self.Fields = []
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("Field"):
            self.Fields.append(Field(tmp.GetIntAttr("XSize"), tmp.GetIntAttr("YSize"),
                        tmp.GetIntAttr("X0"), tmp.GetIntAttr("Y0"), tmpTheme))
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
        
        #������ �������
        self.Static = []
        if globalvars.LevelSettings.GetTag("Layout").GetCountTag("Counter")>0:
            self.Static.append(MakeSimpleSprite(tmpTheme["counter"], Layer_Counter,
                globalvars.LevelSettings.GetTag("Layout").GetTag("Counter").GetIntAttr("x"),
                globalvars.LevelSettings.GetTag("Layout").GetTag("Counter").GetIntAttr("y")))
        #��������� ������ ��� �������
        if globalvars.LevelSettings.GetTag("Layout").GetCountTag("BonusPane")>0:
            tmpX0 = globalvars.LevelSettings.GetTag("Layout").GetTag("BonusPane").GetIntAttr("x")
            tmpY0 = globalvars.LevelSettings.GetTag("Layout").GetTag("BonusPane").GetIntAttr("y")
            tmpSize = globalvars.LevelSettings.GetTag("Layout").GetTag("BonusPane").GetIntAttr("size")
            self.Static.append(MakeSimpleSprite(tmpTheme["bonuspane"], Layer_Deco, tmpX0, tmpY0, scraft.HotspotCenter, 0))
            for i in range(tmpSize):
                self.Static.append(MakeSimpleSprite(tmpTheme["bonuspane"], Layer_Deco,
                        tmpX0+(i+1)*Const_BonusPaneDx, tmpY0+(i+1)*Const_BonusPaneDy,
                        scraft.HotspotCenter, 1))
            self.Static.append(MakeSimpleSprite(tmpTheme["bonuspane"], Layer_Deco,
                    tmpX0 + (tmpSize+1)*Const_BonusPaneDx, tmpY0 + (tmpSize+1)*Const_BonusPaneDy,
                    scraft.HotspotCenter, 2))
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("Decoration"):
            self.Static.append(MakeSimpleSprite(tmp.GetStrAttr("type"), Layer_Deco, tmp.GetIntAttr("x"), tmp.GetIntAttr("y")))
        
        self.TrashCans = []
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("TrashCan"):
            self.TrashCans.append(TrashCan(globalvars.LevelSettings.GetTag("Layout").GetTag("TrashCan").GetIntAttr("size"),
                                globalvars.LevelSettings.GetTag("Layout").GetTag("TrashCan").GetIntAttr("x"),
                                globalvars.LevelSettings.GetTag("Layout").GetTag("TrashCan").GetIntAttr("y"), tmpTheme))
            
        #���������� �����-����
        self.PowerUpButtons = {}
        self.BuyPowerUpButtons = {}
        for tmp in globalvars.LevelSettings.GetTag("Layout").Tags("PowerUp"):
            self.PowerUpButtons[tmp.GetStrAttr("type")] = PushButton("", self,
                Cmd_UsePowerUp + globalvars.GameSettings["powerups"].index(tmp.GetStrAttr("type")),
                PState_Game, u"powerup.use.button", [0, 1, 2, 3], Layer_InterfaceBtn,
                tmp.GetIntAttr("x"), tmp.GetIntAttr("y"), 60, 60, globalvars.PowerUpsInfo[tmp.GetStrAttr("type")]["symbol"],
                [u"powerups", u"powerups.roll", u"powerups.roll", u"powerups.inert"])
            self.BuyPowerUpButtons[tmp.GetStrAttr("type")] = PushButton("", self,
                Cmd_BuyPowerUp + globalvars.GameSettings["powerups"].index(tmp.GetStrAttr("type")),
                PState_Game, u"powerup.buy.button", [0, 1, 2, 3], Layer_InterfaceBtn+1,
                tmp.GetIntAttr("x") + Const_BuyPowerUpButton_Dx, tmp.GetIntAttr("y") + Const_BuyPowerUpButton_Dy, 40, 30,
                u"$"*int(globalvars.PowerUpsInfo[tmp.GetStrAttr("type")]["price"]),
                [u"powerups", u"powerups.roll", u"powerups.roll", u"powerups.inert"])
            self.HasPowerUps[tmp.GetStrAttr("type")] = 0
        self._UpdatePowerUpButtons()
            
        tmpFreeStations = filter(lambda x: x.State == CStationState_Free, self.CStations)
        if tmpFreeStations != []:
            self.CustomersQue.SetState(QueState_Active)
        
        #���������� ����
        for tmp in self.Fields:
            tmp.InitialFilling()
        
        self._SetState(GameState_StartLevel)
        self._SetGameCursorState(GameCursorState_Default)
        
    #--------------------------
    # ��������� ���������� ���������� � ��������� ��������
    #--------------------------
    def _NextCustomerTo(self, station):
        station.SetState(CStationState_Busy)
        station.AttachCustomer(self.CustomersQue.PopCustomer())
        self.RemainingCustomers -= 1
        
    #--------------------------
    # ��������� �������� ������
    #--------------------------
    def SendCommand(self, cmd, parameter = None):
        if cmd == Cmd_Menu:
            globalvars.GUI.CallInternalMenu() 
            oE.PlaySound(u"click", Channel_Default)
            
        if cmd == Cmd_MovementFinished:
            if self.State == GameState_StartLevel:
                self._SetState(GameState_Play)
            
        elif cmd == Cmd_ClickStation:
            if self.GameCursorState == GameCursorState_Tokens:
                if parameter["hasOrder"] and not parameter["mealReady"]:
                    tmpFrom = self.TokensFrom
                    tmpDeltaScore = parameter["station"].AddTokens(self.PickedTokens, self.PickedTokensNo)
                    self.AddScore(tmpDeltaScore)
                    self.TokensFrom.RemoveTokens()
                    self.SendCommand(Cmd_DropWhatYouCarry)
                    if tmpFrom in self.Fields:
                        tmpFrom.SetState(FieldState_Collapse)
                    
            #����� - ������������ �����
            elif self.GameCursorState == GameCursorState_Tool:
                if self.PickedTool == 'Sweet':
                    self.UseTool()
                    parameter["station"].Customer.GiveSweet()
                elif self.PickedTool == 'Gift':
                    self.UseTool()
                    parameter["station"].Customer.GiveGift()
                
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
                self._DropTool()
            
        elif cmd == Cmd_PickFromStorage:
            self._PickTokensFrom(parameter["where"], parameter["type"], parameter["no"])
            
        elif cmd == Cmd_PickFromConveyor:
            if self.GameCursorState == GameCursorState_Tokens:
                if self.TokensFrom != None:
                    #self.TokensFrom.SendCommand(Cmd_ReturnToConveyor,
                    #                { "type": self.PickedTokens, "position": parameter["position"] })
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
            else:
                print "last customer"
                
        #������� �����-���
        elif cmd in range(Cmd_BuyPowerUp, Cmd_BuyPowerUp+len(globalvars.GameSettings["powerups"])):
            type = globalvars.GameSettings["powerups"][cmd - Cmd_BuyPowerUp]
            self.HasPowerUps[type] += 1
            self.Approval -= globalvars.PowerUpsInfo[type]["price"]
            self._UpdatePowerUpButtons()
            self._UpdateLevelInfo()
            
        #������������� �����-���
        elif cmd in range(Cmd_UsePowerUp, Cmd_UsePowerUp+len(globalvars.GameSettings["powerups"])):
            type = globalvars.GameSettings["powerups"][cmd - Cmd_UsePowerUp]
            if type == 'Supersweet':
                self.UseTool('Supersweet')
                for tmp in self.CStations:
                    tmp.Customer.GiveSweet()
            elif type == 'Shuffle':
                self.UseTool('Shuffle')
                for tmp in self.Fields:
                    tmp.SetState(FieldState_Shuffle)
            elif type in ('Cross', 'Gift', 'Spoon', 'Sweet', 'Magicwand'):
                self._PickTool(type)
        
    def AddScore(self, delta):
        self.LevelScore += delta
        self.Approval = min(self.Approval+delta*globalvars.GameSettings["approvalperdollar"],
                            globalvars.GameSettings["maxapproval"])
        self._UpdatePowerUpButtons()
        self._UpdateLevelInfo()
        if self.LevelScore >= globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("moneygoal") and not self.Expert:
            self._SwitchToExpert()
    
    #--------------------------
    # ������ ��������� ����
    #--------------------------
    def _SetState(self, state, parameter = None):
        self.State = state
        if state == GameState_None:
            pass
            
        #������ ������; ������ ������ ��������� ������ �� ����
        elif state == GameState_StartLevel:
            for tmp in self.Fields:
               tmp.SetState(FieldState_StartLevel)
            self._SetState(GameState_Play)
            pass
            
        #�������� ���� - ����
        elif state == GameState_Play:
            pass
                
        #����� ������; ������ ������ �������� ������ � ����
        elif state == GameState_EndLevel:
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
    # �������� ����
    #--------------------------
    def _OnExecute(self, que) :
        try:
            if self.State == GameState_StartLevel:
                pass
                
            elif self.State == GameState_Play:
                #������� ������� ��� ������ ������ �� ����
                if self.GameCursorState == GameCursorState_Tokens:
                    self.TokenSprite.x = oE.mouseX
                    self.TokenSprite.y = oE.mouseY
                elif self.GameCursorState == GameCursorState_Tool:
                    self.ToolSprite.x = oE.mouseX
                    self.ToolSprite.y = oE.mouseY
                #�������� �� ����� ������
                if self.RemainingCustomers == 0:
                    tmpBusyStations = filter(lambda x: x.State == CStationState_Busy, self.CStations)
                    if tmpBusyStations == []:
                        self._SetState(GameState_EndLevel)
                
            elif self.State == GameState_EndLevel:
                #�������� ������� ������ � ����� ������, �� �������� ���������
                self._SetState(GameState_None)
            
            #self._UpdateLevelInfo()
            
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        return scraft.CommandStateRepeat
        
    #--------------------------
    # ������ ��������� �������� ������� (���������, ������ ������, ������ ���)
    #--------------------------
    def _SetGameCursorState(self, state):
        self.GameCursorState = state
        
    #--------------------------
    # ��������� ������ ������
    #--------------------------
    def _PickTool(self, type):
        self.SendCommand(Cmd_DropWhatYouCarry)
        #self.ToolSprite = MakeSprite(globalvars.PowerUpsInfo[type]["src"], Layer_Tools)
        self.ToolSprite = MakeSprite(u"powerups", Layer_Tools, {"text": globalvars.PowerUpsInfo[type]["symbol"]})
        self.PickedTool = type
        self._SetGameCursorState(GameCursorState_Tool)
    
    #--------------------------
    # ���������� ������ ������ (�����)
    #--------------------------
    def _DropTool(self):
        self.ToolSprite.Dispose()
        self.ToolSprite = None
        self.PickedTool = ""
        self._SetGameCursorState(GameCursorState_Default)
        
    #--------------------------
    # ������������� (������) ������
    #--------------------------
    def UseTool(self, tool = ""):
        if tool == "":
            tool = self.PickedTool
        self.HasPowerUps[tool] -= 1
        self._UpdatePowerUpButtons()
        if tool not in ('Supersweet', 'Shuffle'):
            self._DropTool()
        
    def _PickFromConveyor(self, where, type):
        self.PickedTokens = type
        self.PickedTokensNo = 1
        self.TokenSprite = MakeSprite(globalvars.CuisineInfo["Ingredients"][type]["src"], Layer_Tools)
        self.TokensNoSprite = MakeSprite("domcasual-11", Layer_Tools-1,
                                        { "parent": self.TokenSprite, "x": 20, "y": 30, "text": "",
                                          "hotspot": scraft.HotspotCenter, "cfilt-color": 0x000000 })
        self._SetGameCursorState(GameCursorState_Tokens)
        self.TokensFrom = where
        
        
    def _PickTokensFrom(self, where, type, no):
        self.PickedTokens = type
        self.PickedTokensNo = no
        self.TokenSprite = MakeSprite(globalvars.CuisineInfo["Ingredients"][type]["src"], Layer_Tools)
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
        
    def _UpdateLevelInfo(self):
        self.HudElements["Score"].text = unicode(str(self.LevelScore))
        self.HudElements["Approval"].text = unicode("$"*int(self.Approval))
        
    def _SwitchToExpert(self):
        self.HudElements["GoalText"].text = unicode(Str_HUD_ExpertText)
        self.HudElements["Goal"].text = unicode(str(globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("expertgoal")))
        self.Expert = True
        
    def _UpdatePowerUpButtons(self):
        #update powerup buttons
        for tmp in self.HasPowerUps.keys():
            if self.HasPowerUps[tmp] > 0:
                self.PowerUpButtons[tmp].SetState(ButtonState_Up)
                self.BuyPowerUpButtons[tmp].SetState(ButtonState_Inert)
            else:
                self.PowerUpButtons[tmp].SetState(ButtonState_Inert)
                if self.Approval >= globalvars.PowerUpsInfo[tmp]["price"]:
                    self.BuyPowerUpButtons[tmp].SetState(ButtonState_Up)
                else:
                    self.BuyPowerUpButtons[tmp].SetState(ButtonState_Inert)
        
    #--------------------------
    # ������� �������� ����
    #--------------------------
    def Clear(self):
        oE.executor.GetQueue(self.QueNo).Suspend()
        self.Playing = False
        if self.GameCursorState == GameCursorState_Tokens:
            self.TokenSprite.Dispose()
            self.TokensNoSprite.Dispose()
        elif self.GameCursorState == GameCursorState_Tool:
            self.ToolSprite.Dispose()
        
        for tmp in self.PowerUpButtons.values() + self.BuyPowerUpButtons.values():
            tmp.Kill()
        self.PowerUpButtons = {}
        self.BuyPowerUpButtons = {}
            
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
            
        #for tmp in self.CStations + self.Stores:
        #    del tmp
             
    def Show(self, flag):
        """
        �������� - ��������
        """    
        self.BgSprite.visible = flag
        self.BgReceptor.visible = flag
        for spr in self.HudElements.values():
            spr.visible = flag
        for btn in self.GameButtons.values() + self.PowerUpButtons.values() + self.BuyPowerUpButtons.values():
            btn.Show(flag)
        #if self.Playing:
        #    self.CustomersQue.Show(flag)
        #    for tmp in self.CStations:
        #        tmp.Show(flag)
        
    def Freeze(self, flag):
        """
        ���������� �����
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
            #for tmp in self.CStations:
            #    tmp.Freeze(flag)
        
def _ListIntersection(list1, list2):
    return filter(lambda x: x in list2, list1)

