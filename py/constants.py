#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Project: Master Chef
Константы для игры
"""

#---------
# команды
#---------
Cmd_Menu = 1
Cmd_MovementFinished = 2
Cmd_DropWhatYouCarry = 3
Cmd_PickFromStorage = 4
Cmd_ClickStorage = 5
Cmd_ClickStation = 6
Cmd_NewOrder = 7
Cmd_FlopOrder = 8
Cmd_NewCustomer = 9
Cmd_CustomerServed = 10
Cmd_CustomerLost = 11
Cmd_ReleaseCustomer = 12
Cmd_TakeMoney = 13
Cmd_FreeStation = 14
Cmd_PickToken = 15
Cmd_CollapsoidFull = 16
Cmd_CustomerGoesAway = 17
Cmd_PickFromConveyor = 18
Cmd_ReturnToConveyor = 19
Cmd_CollapsoidFashShift = 20
Cmd_CollapsoidBurn = 21
Cmd_Station_DeleteCustomer = 22
Cmd_Station_DeleteCustomerAndLoseMoney = 23
Cmd_Customer_SayThankYou = 24
Cmd_DebugFinishLevel = 25
Cmd_DebugLastCustomer = 26
Cmd_DebugLoseLevel = 27
Cmd_StopDropper = 30                    #команда посылается коллапсоиду, чтобы завершить выброс новых токенов,
                                        #когда все покупатели обслужены (то есть отдавать токены некуда)

Cmd_PickPowerUp = 60
Cmd_UtilizePowerUp = 61
Cmd_UsePowerUp = 70
Cmd_BuyPowerUp = 80

Cmd_TrashCan = 96
Cmd_CustomerStation = 97
Cmd_Storage = 98
Cmd_BgReceptor = 99
Cmd_Receptor = 100

#слои
Layer_BgReceptor = 101
Layer_Receptors = 100
Layer_GameBg = 89
Layer_Door = 88
Layer_CustomersQue = 87   #очередь покупателей
Layer_Counter = 75        #стойка
Layer_Deco = 86           #декорации
Layer_RecipeInfo = 82     #панель инормации о рецепте
Layer_Indicators = 81     #состав рецепта
Layer_Customer = 80       #покупатели
Layer_Hero = 79           #повар
Layer_Station = 78        #столик и инфо-табличка
Layer_Recipe = 76         #рецепт
Layer_RecipeFrame = 75    #рамка над рецептом
Layer_Storage = 70
Layer_StorageFrame = 70
Layer_StorageBg = 69
Layer_Tokens = 55
Layer_CollapsoidScrollButton = 54
Layer_HighlightMarkers = 53
Layer_SelectMarkers = 52
Layer_Tools = 1
Layer_InterfaceBg = 80
Layer_InterfaceBtn = 79
Layer_InterfaceTxt = 78
Layer_InterfaceTools = 75
Layer_Popups = 52
Layer_Particles = 51

#теги для черной доски
BBTag_Ingredients = 0
BBTag_Recipes = 1
BBTag_Cursor = 2

#состояния игры
GameState_None = 0
GameState_StartLevel = 1
GameState_Play = 2
GameState_EndLevel = 3

#состояния игрового поля
FieldState_None = 0
FieldState_StartLevel = 1
FieldState_Input = 2
FieldState_Collapse = 3
FieldState_Shuffle = 4
FieldState_MagicWandConverting = 5
FieldState_EndLevel = 10

Const_HighlightNone = -1
Const_HighlightPick = 0
Const_HighlightAct = 40
Const_HighlightUse = 80

#состояния выбрасывальщика токенов в коллапсоиде
DropperState_None = 0
DropperState_Drop = 1   #выброс токенов
DropperState_Burn = 2   #задержка сдвига для сжигания верхних рядов
DropperState_Move = 3   #сдвиг поля
DropperState_ScrollBack = 4   #обратный скроллинг

#состояния игрового курсора
GameCursorState_Default = 0
GameCursorState_Tokens = 1
GameCursorState_Tool = 2

#состояния кастомера
CustomerState_None = -1
CustomerState_Queue = 0         #
CustomerState_Ordering = 1      #
CustomerState_Wait = 2          #
CustomerState_GoAway = 3        #
CustomerState_MealReady = 4     #
CustomerState_ThankYou = 5      #
CustomerState_GotGift = 6       #

#состояния стейшена
CStationState_None = -1
CStationState_Free = 0
CStationState_AwaitingCustomer = 1
CStationState_Busy = 2

#состояния очереди покупателей
QueState_None = 0
QueState_Active = 1
QueState_Passive = 2

#------------
# координаты
#------------

Crd_QueueMarker_TextX = 298
Crd_QueueMarker_TextY = 37
Crd_QueueMarker_TabletDx = 0
Crd_QueueMarker_TabletDy = -23
Crd_QueueCustomerDx = 42
Crd_QueueCustomerDy = 0

Crd_DoorX = 0
Crd_DoorY = 50

Crd_StationDummyWidth = 140
Crd_StationDummyHeight = 160
Crd_StationDummyDx = 34
Crd_StationDummyDy = -40
Crd_Indicator_DeltaX = 60
Crd_Indicator_DeltaY = -90
Crd_IndicatorScaleXY = 50
Crd_IndicatorText_DeltaX = 20
Crd_IndicatorSign_DeltaY = 30
Crd_HeroDx = 70
Crd_HeroDy = 2
Crd_CustomerDx = 0
Crd_CustomerDy = 7
Crd_HeartsDx = -26
Crd_HeartsDy = 28
Crd_HeartSpritesDx = 13
Crd_HeartSpritesDy = 0
Crd_RecipeSpriteDx = -31
Crd_RecipeSpriteDy = -33
Crd_RecipeSpriteWidth = 62
Crd_RecipeSpriteHeight = 54
Crd_RecipeInfoSpriteDx = 75
Crd_RecipeInfoSpriteDy = -42
Crd_RecipeMaskDx = 0
Crd_RecipeMaskDy = -6

Crd_CharIntroPositions = [(409,270), (350,260), (275,250), (200,260),
    (130,270), (60,330), (50,460), (130,580)]
Crd_CharOutroPositions = { 4: [(80,290), (180,290), (280,290), (380,290)], 2: [(130,290), (330,290)], 1: [(230, 290)] }

#координаты относительно курсора
Crd_ToolSpriteDx = 27
Crd_ToolSpriteDy = 0
Crd_TokenSpriteDx = 27
Crd_TokenSpriteDy = 4
Crd_TokenNoSpriteDx = 43
Crd_TokenNoSpriteDy = 19


Crd_ReleaseButtonDx = 75
Crd_ReleaseButtonDy = 15

Const_MinimalGroup = 1
Const_MaxHearts = 5
Const_EmptyCell = "nothing"
Const_VisibleCustomers = 7

MatchDeltas = [(0,-1), (-1,0), (0,1), (1,0)]
Indexes = { "Col": 0, "Row": 1 }

CFilt_White = 0xFFFFFF
CFilt_Red = 0xFFDDCC
CFilt_Grey = 0x999999
