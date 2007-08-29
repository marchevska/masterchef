#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Project: Master Chef
Список констант и состояний для кнопок/ГУИ
"""

#-----------
# не менять
#-----------
Cmd_None = -1
Cmd_IGM_Resume = 211
Cmd_IGM_Restart = 212
Cmd_IGM_Options = 213
Cmd_IGM_EndGame = 214

Cmd_DevLogoClose = 306
Cmd_PubLogoClose = 307

Cmd_Background = 0
Cmd_Menu_PlayCareer = 300
Cmd_Menu_PlayEndless = 308
Cmd_Menu_Players = 301
Cmd_Menu_Options = 302
Cmd_Menu_Rules = 303
Cmd_Menu_Cookbook = 304
Cmd_Menu_Hiscores = 306
Cmd_Menu_Quit = 305
Cmd_Menu_AskQuit = 309

Cmd_HelpNext = 310
Cmd_HelpPrev = 311
Cmd_HelpClose = 312

Cmd_PlayersRemove = 320
Cmd_PlayersNew = 325
Cmd_PlayersOk = 321
Cmd_PlayersCancel = 322
Cmd_PlayersUp = 323
Cmd_PlayersDown = 324
Cmd_PlayersSelect = 330
Cmd_EnterNameOk = 340
Cmd_EnterNameCancel = 341

Cmd_HiscoresReset = 350
Cmd_HiscoresClose = 351

Cmd_OptionsOk = 360
Cmd_OptionsCancel = 361
Cmd_OptionsMute = 362
Cmd_OptionsHints = 366
Cmd_OptionsFullscreen = 363

Cmd_CookbookNext = 370
Cmd_CookbookPrev = 371
Cmd_CookbookClose = 372

Cmd_SliderDummy = 380
Cmd_Slider = 381

Cmd_Yes = 400
Cmd_No = 401
Cmd_YncYes = 402
Cmd_YncNo = 403
Cmd_YncCancel = 404

Cmd_ContinueYes = 412
Cmd_ContinueNo = 413

Cmd_LvGoalsPlay = 405
Cmd_LvCompleteNextLevel = 414
Cmd_LvCompleteRestart = 419
Cmd_LvCompleteMainMenu = 415

Cmd_EpiCompleteNext = 418
Cmd_EpiCompleteMainMenu = 419

Cmd_ComicsNext = 422
Cmd_IntroNext = 423
Cmd_OutroNext = 424
Cmd_MapStart = 420
Cmd_MapViewResults = 425
Cmd_MapMainMenu = 421
Cmd_MapLevel = 500
Cmd_MapOutro = 570

#состояния всей игры
PState_None = -2
PState_EndGame = -1
PState_DevLogo = 20
PState_PubLogo = 21
PState_MainMenu = 0
PState_Game = 1
PState_InGameMenu = 2
PState_Options = 3
PState_Help = 4
PState_Hiscores = 5
PState_Players = 6
PState_EnterName = 7
PState_StartLevel = 18
PState_NextLevel = 8
PState_EpiComplete = 9
PState_Continue = 11
PState_YesNo = 12
PState_YesNoCancel = 13
PState_Comics = 15
PState_Intro = 23
PState_Outro = 24
PState_MapCareer = 16
PState_MapEndless = 17
PState_Cookbook = 22

#длительность показа логотипов
Time_DevLogoShow = 5000
Time_PubLogoShow = 5000

#состояния курсора
CursorState_None = -1
CursorState_Default = 0
CursorState_Go = 1
CursorState_NoWay = 2

#состояния кнопки
ButtonState_Up = 0
ButtonState_Roll = 1
ButtonState_Down = 2
ButtonState_Inert = 3
ButtonState_Selected = 4

#button frames
Frame_Up = 1    #up state
Frame_Rl = 2    #roll state
Frame_Dn = 3    #down state
Frame_In = 4    #inert state
Frame_Sl = 5    #selected state

#слои для ГУИ
Layer_Tmp = 101
Layer_Background = 100
Layer_Static = 99
Layer_BtnText = 97
Layer_PopupGray = 41
Layer_PopupBg = 40
Layer_PopupStatic = 39
Layer_PopupBtnTxt = 38
Layer_PopupBtnTxt2 = 37
Layer_2ndPopupGray = 31
Layer_2ndPopupBg = 30
Layer_2ndPopupStatic = 29
Layer_2ndPopupBtnTxt = 28
Layer_CursorDown = 10
Layer_CursorUpper = 0
Layer_Cursor = 1

#музыка
MusicState_Menu = 0
MusicState_Game = 1
MusicState_Map = 2
MusicTracks = {
        MusicState_Menu: ["track.menu"],
        MusicState_Game: ["track.game"],
        MusicState_Map: ["track.map"]
}

Channel_Music = 1
Channel_Time = 2
Channel_Default = 0

#разные константы
Const_AllChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
Max_NameLen = 12
Max_Scores = 10


