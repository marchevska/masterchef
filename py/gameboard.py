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
from storage import Store, Field, TrashCan
from extra import *
from customer import *
import levels
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
        self.InventoryText = {}
        self.InventoryText["LevelText"] = MakeTextSprite(u"maiandra14", Layer_InterfaceTxt, 460, 20, scraft.HotspotCenter, Str_HUD_LevelText)
        self.InventoryText["ScoreText"] = MakeTextSprite(u"maiandra14", Layer_InterfaceTxt, 520, 20, scraft.HotspotCenter, Str_HUD_ScoreText)
        self.InventoryText["GoalText"] = MakeTextSprite(u"maiandra14", Layer_InterfaceTxt, 580, 20, scraft.HotspotCenter, Str_HUD_GoalText)
        self.InventoryText["ApprovalText"] = MakeTextSprite(u"maiandra14", Layer_InterfaceTxt, 640, 20, scraft.HotspotCenter, Str_HUD_ApprovalText)
        self.InventoryText["LevelName"] = MakeTextSprite(u"maiandra14", Layer_InterfaceTxt, 460, 50)
        self.InventoryText["Score"] = MakeTextSprite(u"maiandra14", Layer_InterfaceTxt, 520, 50)
        self.InventoryText["Goal"] = MakeTextSprite(u"maiandra14", Layer_InterfaceTxt, 580, 50)
        self.InventoryText["Approval"] = MakeTextSprite(u"powerups", Layer_InterfaceTxt, 640, 50)
        
        #create buttons
        self.GameButtons = {}
        self.GameButtons["Menu"] = PushButton("Menu",
                self, Cmd_Menu, PState_Game,
                u"button-120x40x4st", [0, 1, 2, 3, 4], 
                Layer_InterfaceBtn, 740, 20, 100, 34,
                Str_HUD_MenuButton, [u"maiandra14", u"maiandra14", u"maiandra14", u"maiandra14"])
        
        self.Field = None
        self.CStations = []
        self.Stores = []
        self.Static = []
        self.PickedTool = ""
        self.PickedTokens = ""
        self.PickedTokensNo = 0
        self.TokenSprite = None
        self.ToolSprite = None
        self.PowerUpButtons = {}
        self.BuyPowerUpButtons = {}
        self.HasPowerUps = {}
        self.TokensFrom = None
        
        self.Show(False)
        self.MyRand = oE.NewRandomizer()
        self._SetState(GameState_None)
        self._SetGameCursorState(GameCursorState_Default)
        oE.executor.Schedule(self)
        
    def LaunchLevel(self, no):
        self.Load(no)
        self._StartLevel()
        #self.SaveGame()
        
    def _StartLevel(self):
        self.Expert = False
        self.InventoryText["LevelName"].text = unicode(self.LevelName)
        self.InventoryText["GoalText"].text = unicode(Str_HUD_GoalText)
        self.InventoryText["Goal"].text = unicode(str(globalvars.LevelSettings["moneygoal"]))
        self._UpdateLevelInfo()
        
    def Restart(self):
        #globalvars.CurrentPlayer["Lives"] -= 1
        self.LaunchLevel(self.LevelNo)
        
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
    def Load(self, no):
        
        try:
            tmpLevelFileName = filter(lambda x: globalvars.LevelProgress[x]["no"] == no, globalvars.LevelProgress.keys())[0]
        except:
            print "no such level file"
            sys.exit()
            
        defs.ReadLevelSettings(tmpLevelFileName)
        
        self.LevelNo = 0
        self.LevelScore = 0
        self.Approval = 0
        self.LevelName = globalvars.LevelProgress[tmpLevelFileName]["name"]
        
        self.HasPowerUps = {}
        
        tmpTheme = globalvars.ThemesInfo[globalvars.Layout["Theme"]]
        self.BgSprite.ChangeKlassTo(unicode(tmpTheme["background"]))
        
        #reset customer dispatcher
        self.RemainingCustomers = globalvars.LevelSettings["nocustomers"]
        self.CustomersQue = CustomersQue(tmpTheme)
        
        #размещение стейшенов 
        for tmp in globalvars.Layout["CustomerStations"]:
            tmpStation = CustomerStation(tmp["x"], tmp["y"], tmpTheme)
            if tmp["occupied"]:
                self._NextCustomerTo(tmpStation)
            else:
                tmpStation.SetState(CStationState_Free)
            self.CStations.append(tmpStation)
        
        #игровое поле
        tmp = globalvars.Layout["Field"]
        self.Field = Field(tmp["XSize"], tmp["YSize"], tmp["X0"], tmp["Y0"], tmpTheme)
            
        #размещение складов
        for tmp in globalvars.Layout["Stores"]:
            self.Stores.append(Store(tmp["XSize"], tmp["YSize"], tmp["X0"], tmp["Y0"], tmpTheme))
        
        #прочие объекты
        self.Static = []
        self.Static.append(MakeSimpleSprite(tmpTheme["counter"], Layer_Counter, globalvars.Layout["Counter"]["x"], globalvars.Layout["Counter"]["y"]))
        #составная панель для бонусов
        self.Static.append(MakeSimpleSprite(tmpTheme["bonuspane"], Layer_Deco,
                globalvars.Layout["BonusPane"]["x"], globalvars.Layout["BonusPane"]["y"],
                scraft.HotspotCenter, 0))
        for i in range(globalvars.Layout["BonusPane"]["size"]):
            self.Static.append(MakeSimpleSprite(tmpTheme["bonuspane"], Layer_Deco,
                    globalvars.Layout["BonusPane"]["x"]+(i+1)*Const_BonusPaneDx,
                    globalvars.Layout["BonusPane"]["y"]+(i+1)*Const_BonusPaneDy,
                    scraft.HotspotCenter, 1))
        self.Static.append(MakeSimpleSprite(tmpTheme["bonuspane"], Layer_Deco,
                globalvars.Layout["BonusPane"]["x"]+(globalvars.Layout["BonusPane"]["size"]+1)*Const_BonusPaneDx,
                globalvars.Layout["BonusPane"]["y"]+(globalvars.Layout["BonusPane"]["size"]+1)*Const_BonusPaneDy,
                scraft.HotspotCenter, 2))
        for tmp in globalvars.Layout["Decorations"]:
            self.Static.append(MakeSimpleSprite(unicode(tmp["type"]), Layer_Deco, tmp["x"], tmp["y"]))
        
        self.TrashCan = TrashCan(globalvars.Layout["TrashCan"]["size"], globalvars.Layout["TrashCan"]["x"],
                                 globalvars.Layout["TrashCan"]["y"], tmpTheme)

        #размещение повер-апов
        self.PowerUpButtons = {}
        self.BuyPowerUpButtons = {}
        for tmp in globalvars.Layout["PowerUps"]:
            self.PowerUpButtons[tmp["type"]] = PushButton("", self,
                Cmd_UsePowerUp + globalvars.GameSettings["powerups"].index(tmp["type"]),
                PState_Game, u"powerup.use.button", [0, 1, 2, 3], Layer_InterfaceBtn,
                tmp["x"], tmp["y"], 60, 60, globalvars.PowerUpsInfo[tmp["type"]]["symbol"],
                [u"powerups", u"powerups.roll", u"powerups.roll", u"powerups.inert"])
            self.BuyPowerUpButtons[tmp["type"]] = PushButton("", self,
                Cmd_BuyPowerUp + globalvars.GameSettings["powerups"].index(tmp["type"]),
                PState_Game, u"powerup.buy.button", [0, 1, 2, 3], Layer_InterfaceBtn+1,
                tmp["x"] + Const_BuyPowerUpButton_Dx, tmp["y"] + Const_BuyPowerUpButton_Dy, 40, 30,
                u"$"*int(globalvars.PowerUpsInfo[tmp["type"]]["price"]),
                [u"powerups", u"powerups.roll", u"powerups.roll", u"powerups.inert"])
            self.HasPowerUps[tmp["type"]] = 0
        self._UpdatePowerUpButtons()
            
        tmpFreeStations = filter(lambda x: x.State == CStationState_Free, self.CStations)
        if tmpFreeStations != []:
            self.CustomersQue.SetState(QueState_Active)
        
        #заполнение поля
        self.Field.InitialFilling()
        
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
            
        elif cmd == Cmd_ClickStation:
            if self.GameCursorState == GameCursorState_Tokens:
                tmpFrom = self.TokensFrom
                tmpDeltaScore = parameter.AddTokens(self.PickedTokens, self.PickedTokensNo)
                self.AddScore(tmpDeltaScore)
                self.TokensFrom.RemoveTokens()
                self.SendCommand(Cmd_DropWhatYouCarry)
                if tmpFrom == self.Field:
                    self.Field.SetState(FieldState_Collapse)
                    
            elif self.GameCursorState == GameCursorState_Tool:
                if self.PickedTool == 'Sweet':
                    self.UseTool()
                    parameter.Customer.GiveSweet()
                elif self.PickedTool == 'Gift':
                    self.UseTool()
                    parameter.Customer.GiveGift()
            #иначе - использовать бонус
                
        elif cmd == Cmd_ClickStorage:
            if self.GameCursorState == GameCursorState_Tokens:
                if parameter.HasFreeSlots(self.PickedTokensNo):# and self.TokensFrom == self:
                    tmpFrom = self.TokensFrom
                    tmpType = self.PickedTokens
                    tmpNo = self.PickedTokensNo
                    tmpFrom.RemoveTokens()
                    self.SendCommand(Cmd_DropWhatYouCarry)
                    parameter.AddTokens(tmpType, tmpNo)
                    if tmpFrom == self.Field:
                        self.Field.SetState(FieldState_Collapse)
            
        elif cmd == Cmd_TrashCan:
            if self.GameCursorState == GameCursorState_Tokens:
                tmpFrom = self.TokensFrom
                tmpNo = self.PickedTokensNo
                self.TokensFrom.RemoveTokens()
                self._DropTokensTo(tmpFrom)
                parameter.Discard(tmpNo)
                if tmpFrom == self.Field:
                    self.Field.SetState(FieldState_Collapse)
            
        elif cmd == Cmd_DropWhatYouCarry:
            if self.GameCursorState == GameCursorState_Tokens:
                if self.TokensFrom != None:
                    self._DropTokensTo(self.TokensFrom)
            elif self.GameCursorState == GameCursorState_Tool:
                self._DropTool()
            
        elif cmd == Cmd_PickFromStorage:
            self._PickTokensFrom(parameter["where"], parameter["type"], parameter["no"])
            
        elif cmd == Cmd_NewCustomer:
            tmpFreeStations = filter(lambda x: x.State == CStationState_Free, self.CStations)
            self._NextCustomerTo(choice(tmpFreeStations))
            if self.RemainingCustomers > 0 and len(tmpFreeStations) > 1:
                self.CustomersQue.SetState(QueState_Active)
                
        #elif cmd == Cmd_NewOrder:
        #    parameter.PutOrder(self.RecipesList.pop(0))
        #    
        elif cmd == Cmd_FreeStation:
            if self.RemainingCustomers > 0:
                self.CustomersQue.SetState(QueState_Active)
            else:
                print "last customer"
                
        #покупка повер-апа
        elif cmd in range(Cmd_BuyPowerUp, Cmd_BuyPowerUp+len(globalvars.GameSettings["powerups"])):
            type = globalvars.GameSettings["powerups"][cmd - Cmd_BuyPowerUp]
            self.HasPowerUps[type] += 1
            self.Approval -= globalvars.PowerUpsInfo[type]["price"]
            self._UpdatePowerUpButtons()
            self._UpdateLevelInfo()
            
        #использование повер-апа
        elif cmd in range(Cmd_UsePowerUp, Cmd_UsePowerUp+len(globalvars.GameSettings["powerups"])):
            type = globalvars.GameSettings["powerups"][cmd - Cmd_UsePowerUp]
            if type == 'Supersweet':
                self.UseTool('Supersweet')
                for tmp in self.CStations:
                    tmp.Customer.GiveSweet()
            elif type == 'Shuffle':
                self.UseTool('Shuffle')
                self.Field.SetState(FieldState_Shuffle)
            elif type in ('Cross', 'Gift', 'Spoon', 'Sweet', 'Magicwand'):
                self._PickTool(type)
        
    def AddScore(self, delta):
        self.LevelScore += delta
        self.Approval = min(self.Approval+delta*globalvars.GameSettings["approvalperdollar"],
                            globalvars.GameSettings["maxapproval"])
        self._UpdatePowerUpButtons()
        self._UpdateLevelInfo()
        if self.LevelScore >= globalvars.LevelSettings["moneygoal"] and not self.Expert:
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
            self.Field.SetState(FieldState_StartLevel)
            
        #основной цикл - игра
        elif state == GameState_Play:
            pass
                
        #конец уровня; задать способ удаления блоков с поля
        elif state == GameState_EndLevel:
            pass
        
        
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
    def _PickTool(self, type):
        self.SendCommand(Cmd_DropWhatYouCarry)
        #self.ToolSprite = MakeSprite(globalvars.PowerUpsInfo[type]["src"], Layer_Tools)
        self.ToolSprite = MakeSprite(u"powerups", Layer_Tools, {"text": globalvars.PowerUpsInfo[type]["symbol"]})
        self.PickedTool = type
        self._SetGameCursorState(GameCursorState_Tool)
    
    #--------------------------
    # Сбрасывает иконку бонуса (тулза)
    #--------------------------
    def _DropTool(self):
        self.ToolSprite.Dispose()
        self.ToolSprite = None
        self.PickedTool = ""
        self._SetGameCursorState(GameCursorState_Default)
        
    #--------------------------
    # Использование (расход) бонуса
    #--------------------------
    def UseTool(self, tool = ""):
        if tool == "":
            tool = self.PickedTool
        self.HasPowerUps[tool] -= 1
        self._UpdatePowerUpButtons()
        if tool not in ('Supersweet', 'Shuffle'):
            self._DropTool()
        
    def _PickTokensFrom(self, where, type, no):
        self.PickedTokens = type
        self.PickedTokensNo = no
        self.TokenSprite = MakeSprite(globalvars.CuisineInfo["Ingredients"][type]["src"], Layer_Tools)
        self._SetGameCursorState(GameCursorState_Tokens)
        self.TokensFrom = where
        # добавить текст с числом токенов на курсоре
        
    def _DropTokensTo(self, where):
        if where != None:
            where.DropTokens()
        self.PickedTokens = ""
        self.PickedTokensNo = 0
        self.TokenSprite.Dispose()
        self._SetGameCursorState(GameCursorState_Default)
        self.TokensFrom = None
        
    def _UpdateLevelInfo(self):
        self.InventoryText["Score"].text = unicode(str(self.LevelScore))
        self.InventoryText["Approval"].text = unicode("$"*int(self.Approval))
        
    def _SwitchToExpert(self):
        self.InventoryText["GoalText"].text = unicode(Str_HUD_ExpertText)
        self.InventoryText["Goal"].text = unicode(str(globalvars.LevelSettings["expertgoal"]))
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
        
    def Show(self, flag):
        """
        Показать - спрятать
        """    
        self.BgSprite.visible = flag
        
    def Freeze(self, flag):
        """
        Постановка паузы
        """    
        pass
        
def _ListIntersection(list1, list2):
    return filter(lambda x: x in list2, list1)

