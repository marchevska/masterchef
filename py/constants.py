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
Cmd_DropWhatYouCarry = 7
Cmd_PickFromStorage = 8
Cmd_ClickStorage = 9
Cmd_ClickStation = 10
Cmd_NewOrder = 11
Cmd_FlopOrder = 12
Cmd_NewCustomer = 13
Cmd_ReleaseCustomer = 14
Cmd_FreeStation = 15

Cmd_Station_DeleteCustomer = 20
Cmd_Customer_SayThankYou = 21

Cmd_UsePowerUp = 70
Cmd_BuyPowerUp = 80

Cmd_TrashCan = 96
Cmd_CustomerStation = 97
Cmd_Storage = 98
Cmd_BgReceptor = 99
Cmd_Receptor = 100

#слои
Layer_BgReceptor = 102
Layer_Receptors = 101
Layer_GameBg = 89
Layer_CustomersQue = 88   #очередь покупателей
Layer_Counter = 84        #стойка
Layer_Deco = 86           #декорации
Layer_Customer = 85       #покупатели
Layer_Station = 84        #столик и инфо-табличка
Layer_Recipe = 83         #рецепт
#Layer_Order = 85
#Layer_Player = 81
Layer_Storage = 84
Layer_Tokens = 83
Layer_Markers = 82
Layer_Tools = 81
Layer_InterfaceBg = 80
Layer_InterfaceBtn = 79
Layer_InterfaceTxt = 78
Layer_InterfaceTools = 75

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

#состояния игрового курсора
GameCursorState_Default = 0
GameCursorState_Tokens = 1
GameCursorState_Tool = 2

#состояния кастомера
CustomerState_None = -1
CustomerState_Queue = 0
CustomerState_Ordering = 1
CustomerState_Wait = 2
CustomerState_GoAway = 3
CustomerState_ThankYou = 4
CustomerState_GotGift = 5

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

Crd_Queue_X0 = 140
Crd_Queue_Y0 = 125
Crd_QueueCustomerDx = 45
Crd_QueueCustomerDy = 0
Crd_QueueTablet_X0 = 70
Crd_QueueTablet_Y0 = 75
Crd_QueueMarker_X0 = 70
Crd_QueueMarker_Y0 = 60

Crd_StationDummyWidth = 100
Crd_StationDummyHeight = 130
Crd_StationDummyDx = 30
Crd_StationDummyDy = -20
Crd_Indicator_DeltaX = 48
Crd_Indicator_DeltaY = -80
Crd_IndicatorScaleXY = 50
Crd_IndicatorText_DeltaX = 12
Crd_IndicatorSign_DeltaY = 20
Crd_HeroDx = 60
Crd_HeroDy = -3
Crd_CustomerDx = 0
Crd_CustomerDy = 15
Crd_HeartsDx = -24
Crd_HeartsDy = 10
Crd_HeartSpritesDx = 12
Crd_HeartSpritesDy = 0
Crd_RecipeSpriteDx = 0
Crd_RecipeSpriteDy = -7
Crd_RecipeInfoSpriteDx = 55
Crd_RecipeInfoSpriteDy = -37

Crd_ReleaseButtonDx = 55
Crd_ReleaseButtonDy = 15

Const_BonusPaneDx = 0
Const_BonusPaneDy = 50
Const_BuyPowerUpButton_Dx = 40
Const_BuyPowerUpButton_Dy = 0

Const_MinimalGroup = 1
Const_MaxHearts = 5
Const_EmptyCell = "nothing"
Const_VisibleCustomers = 7

MatchDeltas = [(0,-1), (-1,0), (0,1), (1,0)]
Indexes = { "Col": 0, "Row": 1 }

