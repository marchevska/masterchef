#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
ГУИ
"""

import sys
import string
import scraft
from scraft import engine as oE
from configconst import *
from guiconst import *
from guielements import *
from strings import *
import defs
import playerlist
import config
import globalvars
import traceback

class Gui(scraft.Dispatcher):
    def __init__(self):
        globalvars.LastCookie = Cmd_None
        self.LastCookie = Cmd_None
        self.NextStateTime = 0
        self.CurrentHelpPage = 0
        self.TotalHelpPages = 3
        self.FirstPlayer = 0
        self.SelectedPlayer = -1
        self.SelectedLevel = -1
        self.TotalPlayersOnScreen = 6
        self.TotalCareerLevels = 0
        self.SavedOptions = []
        self.LvCompleteSuccess = True
           
        #--------------
        # логотипы разработчика и издателя
        #--------------
        self.DevLogo = { "Static": {}, "Text": {}, "Buttons": {} }
        self.DevLogo["Buttons"]["Back"] = PushButton("",
                self, Cmd_DevLogoClose, PState_DevLogo, u"developer-logo", [0, 0, 0], 
                Layer_Background, 400, 300, 800, 600)
        self.PubLogo = { "Static": {}, "Text": {}, "Buttons": {} }
        self.PubLogo["Buttons"]["Back"] = PushButton("",
                self, Cmd_PubLogoClose, PState_PubLogo, u"publisher-logo", [0, 0, 0], 
                Layer_Background, 400, 300, 800, 600)
           
        #--------------
        # главное меню
        #--------------
        self.MainMenuDialog = { "Static": {}, "Text": {}, "Buttons": {} }
        self.MainMenuDialog["Static"]["Back"] = MakeSimpleSprite(u"main-menu", Layer_Background)
        self.MainMenuDialog["Static"]["Back"].dispatcher = self
        self.MainMenuDialog["Static"]["Back"].cookie = Cmd_Background
        self.MainMenuDialog["Buttons"]["PlayCareer"] = PushButton("PlayCareer",
                self, Cmd_Menu_PlayCareer, PState_MainMenu,
                u"button-4st", [0, 1, 2], 
                Layer_BtnText, 600, 300, 120, 40,
                Str_Menu_PlayCareer, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.MainMenuDialog["Buttons"]["PlayEndless"] = PushButton("PlayEndless",
                self, Cmd_Menu_PlayEndless, PState_MainMenu,
                u"button-4st", [0, 1, 2], 
                Layer_BtnText, 600, 350, 120, 40,
                Str_Menu_PlayEndless, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.MainMenuDialog["Buttons"]["Options"] = PushButton("Options",
                self, Cmd_Menu_Options, PState_MainMenu,
                u"button-4st", [0, 1, 2], 
                Layer_BtnText, 600, 400, 120, 40,
                Str_Menu_Options, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.MainMenuDialog["Buttons"]["Rules"] = PushButton("Help",
                self, Cmd_Menu_Rules, PState_MainMenu,
                u"button-4st", [0, 1, 2], 
                Layer_BtnText, 600, 450, 120, 40,
                Str_Menu_Rules, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        #self.MainMenuDialog["Buttons"]["Highscores"] = PushButton("Hiscores",
        #        self, Cmd_Menu_Hiscores, PState_MainMenu,
        #        u"button-4st", [0, 1, 2], 
        #        Layer_BtnText, 600, 380, 120, 40,
        #        Str_Menu_Hiscores, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.MainMenuDialog["Buttons"]["Quit"] = PushButton("Quit",
                self, Cmd_Menu_Quit, PState_MainMenu,
                u"button-4st", [0, 1, 2], 
                Layer_BtnText, 600, 500, 120, 40,
                Str_Menu_Quit, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.MainMenuDialog["Buttons"]["Players"] = PushButton("Players",
                self, Cmd_Menu_Players, PState_MainMenu,
                u"$spritecraft$dummy$", [0, 0, 0], 
                Layer_BtnText, 200, 500, 240, 40,
                Str_Menu_Players, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.MainMenuDialog["Text"]["WelcomeMessage"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt2, 200, 450)
        
        #---------
        # справка
        #---------
        self.RulesDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.RulesDialog["Static"]["Back"] = MakeSimpleSprite(u"help-page1", Layer_Background)
        self.RulesDialog["Buttons"]["HelpPrev"] = PushButton("HelpPrev",
                self, Cmd_HelpPrev, PState_Help,
                u"button-4st", [0, 1, 2, 3], 
                Layer_BtnText, 100, 540, 120, 40,
                Str_HelpPrev, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down", u"papyrus2-inert"])
        self.RulesDialog["Buttons"]["HelpNext"] = PushButton("HelpNext",
                self, Cmd_HelpNext, PState_Help,
                u"button-4st", [0, 1, 2, 3], 
                Layer_BtnText, 400, 540, 120, 40,
                Str_HelpNext, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down", u"papyrus2-inert"])
        self.RulesDialog["Buttons"]["HelpClose"] = PushButton("HelpClose",
                self, Cmd_HelpClose, PState_Help,
                u"button-4st", [0, 1, 2], 
                Layer_BtnText, 700, 540, 120, 40,
                Str_HelpClose, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        
        #----------------
        # список игроков
        #----------------
        self.PlayersDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.PlayersDialog["Static"]["Back"] = MakeSimpleSprite(u"popup-background", Layer_PopupBg)
        self.PlayersDialog["Text"]["Title"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_Players_Title)
        self.PlayersDialog["Buttons"]["Remove"] = PushButton("PlayersRemove",
                self, Cmd_PlayersRemove, PState_Players,
                u"button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 260, 500, 120, 40,
                Str_PlayersRemove, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down", u"papyrus2-inert"])
        self.PlayersDialog["Buttons"]["Ok"] = PushButton("PlayersOk",
                self, Cmd_PlayersOk, PState_Players,
                u"button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 400, 500, 120, 40,
                Str_PlayersOk, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down", u"papyrus2-inert"])
        self.PlayersDialog["Buttons"]["Cancel"] = PushButton("PlayersCancel",
                self, Cmd_PlayersCancel, PState_Players,
                u"button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 540, 500, 120, 40,
                Str_PlayersCancel, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down", u"papyrus2-inert"])
        self.PlayersDialog["Buttons"]["Up"] = PushButton("PlayersUp",
                self, Cmd_PlayersUp, PState_Players,
                u"players-arrow-up", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 520, 215, 30, 30)
        self.PlayersDialog["Buttons"]["Down"] = PushButton("PlayersDown",
                self, Cmd_PlayersDown, PState_Players,
                u"players-arrow-down", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 520, 405, 30, 30)
        for i in range(self.TotalPlayersOnScreen):
            self.PlayersDialog["Buttons"]["Player_"+str(i)] = PushButton("PlayerNo"+str(i),
                self, Cmd_PlayersSelect+i, PState_Players,
                u"players-select-button", [0, 1, 2, 4, 3], 
                Layer_PopupBtnTxt, 400, 220 + 30 * i, 220, 30,
                "", [u"papyrus2", u"papyrus2-roll", u"papyrus2-down", u"papyrus2", u"papyrus2"])
        
        #------------
        # ввод имени
        #------------
        self.EnterNameDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.EnterNameDialog["Static"]["Back"] = MakeSimpleSprite(u"2nd-popup-background", Layer_2ndPopupBg)
        self.EnterNameDialog["Text"]["Title"] = MakeTextSprite(u"papyrus2", Layer_2ndPopupBtnTxt, 400, 250,
                                                    scraft.HotspotCenterTop, Str_EnterName_Title)
        self.EnterNameDialog["Static"]["TextCursor"] = MakeSimpleSprite(u"textcursor", Layer_2ndPopupBtnTxt, 400, 290)
        self.EnterNameDialog["Static"]["TextCursor"].AnimateLoop(2)
        self.EnterNameDialog["Buttons"]["Ok"] = PushButton("EnterNameOk",
                self, Cmd_EnterNameOk, PState_EnterName,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 330, 360, 120, 40,
                Str_EnterNameOk, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.EnterNameDialog["Buttons"]["Cancel"] = PushButton("EnterNameCancel",
                self, Cmd_EnterNameCancel, PState_EnterName,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 470, 360, 120, 40,
                Str_EnterNameCancel, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.EnterNameDialog["Text"]["Name"] = MakeTextSprite(u"papyrus2", Layer_2ndPopupBtnTxt, 400, 290)
        self.EnterNameDialog["Text"]["NameErrors"] = MakeTextSprite(u"papyrus2", Layer_2ndPopupBtnTxt, 400, 320)
        self.EnterNameDialog["Text"]["NameErrors"].xScale, self.EnterNameDialog["Text"]["NameErrors"].yScale = 50,50
        
        #------------------
        # уровень завершен
        #------------------
        self.LevelCompleteDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.LevelCompleteDialog["Static"]["Back"] = MakeSimpleSprite(u"popup-background", Layer_PopupBg)
        self.LevelCompleteDialog["Text"]["Title"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_LvComplete_Title)
        self.LevelCompleteDialog["Text"]["Text0"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 400, 220)
        self.LevelCompleteDialog["Text"]["Text1"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 300, 270)
        self.LevelCompleteDialog["Text"]["Text2"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 500, 270)
        self.LevelCompleteDialog["Text"]["Text3"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 300, 350)
        self.LevelCompleteDialog["Text"]["Text4"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 500, 350)
        self.LevelCompleteDialog["Buttons"]["NextLevel"] = PushButton("LvCompleteNextLevel",
                self, Cmd_LvCompleteNextLevel, PState_NextLevel,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 500, 120, 40,
                Str_LvCompleteNextLevel, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.LevelCompleteDialog["Buttons"]["No"] = PushButton("LvCompleteMainMenu",
                self, Cmd_LvCompleteMainMenu, PState_NextLevel,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 460, 500, 120, 40,
                Str_LvCompleteMainMenu, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        
        #----------------
        # эпизод пройден
        #----------------
        self.EpisodeCompleteDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.EpisodeCompleteDialog["Static"]["Back"] = MakeSimpleSprite(u"episode1-complete", Layer_PopupBg)
        self.EpisodeCompleteDialog["Buttons"]["Next"] = PushButton("EpiCompleteNext",
                self, Cmd_EpiCompleteNext, PState_EpiComplete,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 155, 120, 40,
                Str_EpiCompleteNext, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.EpisodeCompleteDialog["Buttons"]["MainMenu"] = PushButton("EpiCompleteMainMenu",
                self, Cmd_EpiCompleteMainMenu, PState_EpiComplete,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 460, 155, 120, 40,
                Str_EpiCompleteMainMenu, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.EpisodeCompleteDialog["Text"]["Message"] = MakeTextSprite(u"arial18", Layer_PopupBtnTxt, 320, 200)
        
        #---------------
        # игра окончена
        #---------------
        self.GameOverDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.GameOverDialog["Static"]["Back"] = MakeSimpleSprite(u"popup-background", Layer_PopupBg)
        self.GameOverDialog["Text"]["Title"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_GameOver_Title)
        self.GameOverDialog["Buttons"]["Hiscores"] = PushButton("GameOverHiscores",
                self, Cmd_GameOverHiscores, PState_GameOver,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 500, 120, 40,
                Str_GameOverHiscores, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.GameOverDialog["Buttons"]["MainMenu"] = PushButton("GameOverMainMenu",
                self, Cmd_GameOverMainMenu, PState_GameOver,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 460, 500, 120, 40,
                Str_GameOverMainMenu, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.GameOverDialog["Text"]["Message"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 320, 200)
        
        #---------
        # данетка
        #---------
        self.YesNoDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.YesNoDialog["Static"]["Back"] = MakeSimpleSprite(u"2nd-popup-background", Layer_2ndPopupBg)
        self.YesNoDialog["Text"]["QuestionText"] = MakeTextSprite(u"papyrus2", Layer_2ndPopupBtnTxt, 400, 250, scraft.HotspotCenterTop)
        self.YesNoDialog["Buttons"]["Yes"] = PushButton("Yes",
                self, Cmd_Yes, PState_YesNo,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 330, 360, 120, 40,
                Str_Yes, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.YesNoDialog["Buttons"]["No"] = PushButton("No",
                self, Cmd_No, PState_YesNo,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 470, 360, 120, 40,
                Str_No, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        
        #---------------
        # Yes-No-Cancel
        #---------------
        self.YesNoCancelDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.YesNoCancelDialog["Static"]["Back"] = MakeSimpleSprite(u"2nd-popup-background", Layer_2ndPopupBg)
        self.YesNoCancelDialog["Text"]["QuestionText"] = MakeTextSprite(u"papyrus2", Layer_2ndPopupBtnTxt, 400, 250, scraft.HotspotCenterTop)
        self.YesNoCancelDialog["Buttons"]["Yes"] = PushButton("Yes",
                self, Cmd_YncYes, PState_YesNoCancel,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 260, 360, 120, 40,
                Str_Yes, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.YesNoCancelDialog["Buttons"]["No"] = PushButton("No",
                self, Cmd_YncNo, PState_YesNoCancel,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 400, 360, 120, 40,
                Str_No, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.YesNoCancelDialog["Buttons"]["Cancel"] = PushButton("Cancel",
                self, Cmd_YncCancel, PState_YesNoCancel,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 540, 360, 120, 40,
                Str_Cancel, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        
        #-------
        # опции
        #-------
        self.OptionsDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.OptionsDialog["Static"]["Back"] = MakeSimpleSprite(u"popup-background", Layer_PopupBg)
        self.OptionsDialog["Text"]["Title"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_Options_Title)
        self.OptionsDialog["Text"]["Label_Sound"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 300, 230,
                                                                   scraft.HotspotCenter, Str_Options_LabelSound)
        self.OptionsDialog["Text"]["Label_Music"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 300, 280,
                                                                   scraft.HotspotCenter, Str_Options_LabelMusic)
        self.OptionsDialog["Buttons"]["Slider_Sound"] = Slider("SliderSound", globalvars.GameConfig, 'Sound',
                PState_Options, u"options-slider", [0, 1, 2], 
                Layer_PopupBtnTxt, 400, 250, 250, 40, (310, 490), (250, 250), u"slider-background")
        self.OptionsDialog["Buttons"]["Slider_Music"] = Slider("SliderMusic", globalvars.GameConfig, 'Music',
                PState_Options, u"options-slider", [0, 1, 2], 
                Layer_PopupBtnTxt, 400, 300, 250, 40, (310, 490), (300, 300), u"slider-background")
        self.OptionsDialog["Text"]["Label_Mute"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 335, 343,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelMute)
        self.OptionsDialog["Text"]["Label_Hints"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 335, 373,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelHints)
        self.OptionsDialog["Text"]["Label_Fullscreen"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 335, 403,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelFullscreen)
        self.OptionsDialog["Buttons"]["Mute"] = PushButton("OptionsMute",
                self, Cmd_OptionsMute, PState_Options,
                u"options-checkbox", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 340, 30, 30)
        self.OptionsDialog["Buttons"]["Hints"] = PushButton("OptionsHints",
                self, Cmd_OptionsHints, PState_Options,
                u"options-checkbox", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 370, 30, 30)
        self.OptionsDialog["Buttons"]["Fullscreen"] = PushButton("OptionsFullscreen",
                self, Cmd_OptionsFullscreen, PState_Options,
                u"options-checkbox", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 400, 30, 30)
        self.OptionsDialog["Static"]["Galka_Mute"] = MakeSimpleSprite(u"options-galka", Layer_PopupBtnTxt2, 320, 340)
        self.OptionsDialog["Static"]["Galka_Hints"] = MakeSimpleSprite(u"options-galka", Layer_PopupBtnTxt2, 320, 370)
        self.OptionsDialog["Static"]["Galka_Fullscreen"] = MakeSimpleSprite(u"options-galka", Layer_PopupBtnTxt2, 320, 400)
        self.OptionsDialog["Buttons"]["Ok"] = PushButton("OptionsOk",
                self, Cmd_OptionsOk, PState_Options,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 400, 500, 120, 40,
                Str_OptionsOk, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        #self.OptionsDialog["Buttons"]["Cancel"] = PushButton("Cmd_OptionsCancel",
        #        self, Cmd_OptionsCancel, PState_Options,
        #        u"button-4st", [0, 1, 2], 
        #        Layer_PopupBtnTxt, 460, 500, 120, 40,
        #        Str_OptionsCancel, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.OptionsDialog["Buttons"]["Resume"] = PushButton("OptionsResume",
                self, Cmd_IGM_Resume, PState_Options,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 240, 500, 120, 40,
                Str_OptionsResume, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        self.OptionsDialog["Buttons"]["Restart"] = PushButton("OptionsRestart",
                self, Cmd_IGM_Restart, PState_Options,
                u"button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 400, 500, 120, 40,
                Str_OptionsRestart, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down", u"papyrus2-inert"])
        self.OptionsDialog["Buttons"]["EndGame"] = PushButton("OptionsEndGame",
                self, Cmd_IGM_EndGame, PState_Options,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 540, 500, 120, 40,
                Str_OptionsEndGame, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        
        #---------
        # рекорды
        #---------
        self.HiscoresDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.HiscoresDialog["Static"]["Back"] = MakeSimpleSprite(u"popup-background", Layer_PopupBg)
        self.HiscoresDialog["Text"]["Title"] = MakeTextSprite(u"papyrus2", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_Hiscores_Title)
        self.HiscoresDialog["Buttons"]["Reset"] = PushButton("HiscoresReset",
                self, Cmd_HiscoresReset, PState_Hiscores,
                u"button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 330, 500, 120, 40,
                Str_HiscoresReset, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down", u"papyrus2-inert"])
        self.HiscoresDialog["Buttons"]["Close"] = PushButton("HiscoresClose",
                self, Cmd_HiscoresClose, PState_Hiscores,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 470, 500, 120, 40,
                Str_HiscoresClose, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        for i in range(Max_Scores):
            self.HiscoresDialog["Text"]["Name_"+str(i)] = MakeTextSprite(u"papyrus2",
                Layer_PopupBtnTxt, 280, 220 + 30* i, scraft.HotspotLeftCenter)
            self.HiscoresDialog["Text"]["Score_"+str(i)] = MakeTextSprite(u"papyrus2",
                Layer_PopupBtnTxt, 520, 220 + 30* i, scraft.HotspotRightCenter)
        
        #-------
        # карта карьерного режима
        #-------
        self.MapCareerDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.MapCareerDialog["Static"]["Back"] = MakeSimpleSprite(u"map-background", Layer_Background)
        self.MapCareerDialog["Buttons"]["Start"] = PushButton("MapStart",
                self, Cmd_MapStart, PState_MapCareer,
                u"button-4st", [0, 1, 2, 3], 
                Layer_BtnText, 300, 520, 120, 40,
                Str_MapStart, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down", u"papyrus2-inert"])
        self.MapCareerDialog["Buttons"]["MainMenu"] = PushButton("MapMainMenu",
                self, Cmd_MapMainMenu, PState_MapCareer,
                u"button-4st", [0, 1, 2], 
                Layer_BtnText, 440, 520, 120, 40,
                Str_MapMainMenu, [u"papyrus2", u"papyrus2-roll", u"papyrus2-down"])
        tmpEpisodeIterator = globalvars.LevelProgress.IterateTag(u"Episode")
        i = 0
        while tmpEpisodeIterator.Next():
            i += 1
            tmpEpisodeName = tmpEpisodeIterator.Get().GetContent()
            self.MapCareerDialog["Text"][tmpEpisodeName] = MakeTextSprite(u"papyrus2",
                Layer_PopupBtnTxt, 50, 100*i, scraft.HotspotLeftCenter, tmpEpisodeName)
            tmpLevelIterator = tmpEpisodeIterator.Get().IterateTag(u"level")
            while tmpLevelIterator.Next():
                tmp = tmpLevelIterator.Get()
                tmpLevelFileName = tmp.GetContent()
                tmpLevelNo = int(tmpLevelFileName[4:6])
                self.MapCareerDialog["Buttons"]["Level_"+str(tmpLevelNo)] = PushButton("MapLevel"+str(i),
                    self, Cmd_MapLevel + tmpLevelNo, PState_MapCareer,
                    u"level-pointers", [0, 1, 2, 3, 4], Layer_BtnText,
                    tmp.GetIntAttr(u"x"), tmp.GetIntAttr(u"y"), 30, 30)
                self.TotalCareerLevels += 1
        
        self._SetState(PState_DevLogo)    
        oE.executor.Schedule(self)
        
    def _ShowDialog(self, dialog, flag):
        for spr in dialog["Static"].values() + dialog["Text"].values():
            spr.visible = flag
        for btn in dialog["Buttons"].values():
            btn.Show(flag)
        
    def CallInternalMenu(self):
        self._SetState(PState_Options)
        
    def CallLevelCompleteDialog(self, flag, level=0, score=0, time=0):
        self._SetState(PState_NextLevel)
        self.LvCompleteSuccess = flag
        if flag:
            #self.LevelCompleteDialog["Text"]["Text0"].text = unicode(Str_LvComplete_Passed + \
            #    levels.Levels[level]["Name"])
            self.LevelCompleteDialog["Text"]["Text1"].text = unicode(Str_LvComplete_YourScoreIs + str(score))
            self.LevelCompleteDialog["Text"]["Text2"].text = unicode(Str_LvComplete_YourTimeIs + self._StrMinSec(time))
            self.LevelCompleteDialog["Text"]["Text3"].text = unicode(Str_LvComplete_BestScore + \
                str(globalvars.BestResults[level]["BestScore"]) + \
                Str_LvComplete_AchievedBy + globalvars.BestResults[level]["PlayerScore"])
            self.LevelCompleteDialog["Text"]["Text4"].text = unicode(Str_LvComplete_BestTime + \
                self._StrMinSec(globalvars.BestResults[level]["BestTime"]) + \
                Str_LvComplete_AchievedBy + globalvars.BestResults[level]["PlayerTime"])
            self.LevelCompleteDialog["Buttons"]["NextLevel"].SetText(Str_LvCompleteNextLevel)
        else:
            self.LevelCompleteDialog["Text"]["Text0"].text = unicode(Str_LvComplete_TooLate)
            self.LevelCompleteDialog["Text"]["Text1"].text = u""
            self.LevelCompleteDialog["Text"]["Text2"].text = u""
            self.LevelCompleteDialog["Text"]["Text3"].text = u""
            self.LevelCompleteDialog["Text"]["Text4"].text = u""
            self.LevelCompleteDialog["Buttons"]["NextLevel"].SetText(Str_LvCompleteTryAgain)
        
    def _StrMinSec(self, millis):
        tmpSec = int(millis/1000)%60
        tmpMin = int(millis/60000)
        if tmpSec != 0:
            tmpStr = str(tmpMin) + "." + str(tmpSec)
        else:
            tmpStr = str(tmpMin) + ".00"
        return tmpStr
        
    def _UpdateEpisodeCompleteDialog(self):
        self.EpisodeCompleteDialog["MessageText"].text = levels.Episodes[levels.Levels[globalvars.CurrentPlayer["Level"]]["Episode"]]["CompleteText"]
        
    def CallGameOverDialog(self, flag):
        self._SetState(PState_GameOver)
        
    def _Ask(self, question, answerYes = "Yes", answerNo = "No"):
        self._SetState(PState_YesNo)
        self.YesNoDialog["Text"]["QuestionText"].text = unicode(question)
        self.YesNoDialog["Buttons"]["Yes"].SetText(answerYes)
        self.YesNoDialog["Buttons"]["No"].SetText(answerNo)
        
    def _AskYnc(self, question, answerYes = "Yes", answerNo = "No", answerCancel = "Cancel"):
        self._SetState(PState_YesNoCancel)
        self.YesNoCancelDialog["Text"]["QuestionText"].text = unicode(question)
        self.YesNoCancelDialog["Buttons"]["Yes"].SetText(answerYes)
        self.YesNoCancelDialog["Buttons"]["No"].SetText(answerNo)
        self.YesNoCancelDialog["Buttons"]["Cancel"].SetText(answerCancel)
        
    def _ShowHelpPage(self, no):
        if no == 0:
            self.RulesDialog["Buttons"]["HelpPrev"].SetState(ButtonState_Inert)
        else:
            self.RulesDialog["Buttons"]["HelpPrev"].SetState(ButtonState_Up)
        if no == self.TotalHelpPages-1:
            self.RulesDialog["Buttons"]["HelpNext"].SetState(ButtonState_Inert)
        else:
            self.RulesDialog["Buttons"]["HelpNext"].SetState(ButtonState_Up)
        self.RulesDialog["Static"]["Back"].ChangeKlassTo(u"help-page"+str(no+1))
        self.CurrentHelpPage = no
        
    def _DrawPlayersList(self):
        if globalvars.GameConfig["Player"] != "None":
            tmpName = globalvars.GameConfig["Player"]
            if globalvars.PlList.count(tmpName) > 0:
                tmpInd = globalvars.PlList.index(tmpName)
                self.FirstPlayer = min(tmpInd, len(globalvars.PlList) - self.TotalPlayersOnScreen)
                self.FirstPlayer = max(self.FirstPlayer, 0)
                self.SelectedPlayer = tmpInd
        self._UpdatePlayersList()
                
    def _UpdatePlayersList(self):
        tmpCount = min(self.TotalPlayersOnScreen, len(globalvars.PlList))
        for i in range(tmpCount):
            if self.FirstPlayer + i == self.SelectedPlayer:
                self.PlayersDialog["Buttons"]["Player_"+str(i)].SetState(ButtonState_Selected)
            else:
                self.PlayersDialog["Buttons"]["Player_"+str(i)].SetState(ButtonState_Up)
            self.PlayersDialog["Buttons"]["Player_"+str(i)].Show(True)
            self.PlayersDialog["Buttons"]["Player_"+str(i)].SetText(globalvars.PlList[self.FirstPlayer+i])
        if tmpCount < self.TotalPlayersOnScreen:
            for i in range(tmpCount, self.TotalPlayersOnScreen):
                self.PlayersDialog["Buttons"]["Player_"+str(i)].Show(False)
        if self.FirstPlayer > 0:
            self.PlayersDialog["Buttons"]["Up"].Show(True)
        else:
            self.PlayersDialog["Buttons"]["Up"].Show(False)
        if self.FirstPlayer + self.TotalPlayersOnScreen < len(globalvars.PlList):
            self.PlayersDialog["Buttons"]["Down"].Show(True)
        else:
            self.PlayersDialog["Buttons"]["Down"].Show(False)
        if self.SelectedPlayer >= 0:
            self.PlayersDialog["Buttons"]["Remove"].SetState(ButtonState_Up)
            self.PlayersDialog["Buttons"]["Ok"].SetState(ButtonState_Up)
            self.PlayersDialog["Buttons"]["Cancel"].SetState(ButtonState_Up)
        else:
            self.PlayersDialog["Buttons"]["Remove"].SetState(ButtonState_Inert)
            self.PlayersDialog["Buttons"]["Ok"].SetState(ButtonState_Inert)
            self.PlayersDialog["Buttons"]["Cancel"].SetState(ButtonState_Inert)
        
    def _UpdateHiscoresDialog(self):
        tmpTotalScores = len(globalvars.HiscoresList)
        for i in range(tmpTotalScores):
            tmpScore = globalvars.HiscoresList[i]
            self.HiscoresDialog["Text"]["Name_"+str(i)].text = unicode(tmpScore["Name"])
            self.HiscoresDialog["Text"]["Score_"+str(i)].text = unicode(str(tmpScore["Score"]))
            if tmpScore["Active"]:
                self.HiscoresDialog["Text"]["Name_"+str(i)].cfilt.color = CFilt_CurScore
                self.HiscoresDialog["Text"]["Score_"+str(i)].cfilt.color = CFilt_CurScore
                tmpScore["Active"] = False
            else:
                self.HiscoresDialog["Text"]["Name_"+str(i)].cfilt.color = CFilt_None
                self.HiscoresDialog["Text"]["Score_"+str(i)].cfilt.color = CFilt_None
        if tmpTotalScores < Max_Scores:
            for i in range(tmpTotalScores, Max_Scores):
                self.HiscoresDialog["Text"]["Name_"+str(i)].text = u""
                self.HiscoresDialog["Text"]["Score_"+str(i)].text = u""
        if tmpTotalScores == 0:
            self.HiscoresDialog["Buttons"]["Reset"].SetState(ButtonState_Inert)
        else:
            self.HiscoresDialog["Buttons"]["Reset"].SetState(ButtonState_Up)
        
    def _UpdateOptionsDialog(self):
        tmpCfg = globalvars.GameConfig
        self.OptionsDialog["Static"]["Galka_Fullscreen"].visible = tmpCfg["Fullscreen"]
        self.OptionsDialog["Static"]["Galka_Mute"].visible = tmpCfg["Mute"]
        self.OptionsDialog["Static"]["Galka_Hints"].visible = tmpCfg["Hints"]
        self.OptionsDialog["Buttons"]["Slider_Sound"].SetValue(tmpCfg["Sound"])
        self.OptionsDialog["Buttons"]["Slider_Music"].SetValue(tmpCfg["Music"])
        if globalvars.StateStack[-2] == PState_Game:
            self.OptionsDialog["Buttons"]["Resume"].Show(True)
            self.OptionsDialog["Buttons"]["Restart"].Show(True)
            self.OptionsDialog["Buttons"]["EndGame"].Show(True)
            self.OptionsDialog["Buttons"]["Ok"].Show(False)
        else:
            self.OptionsDialog["Buttons"]["Resume"].Show(False)
            self.OptionsDialog["Buttons"]["Restart"].Show(False)
            self.OptionsDialog["Buttons"]["EndGame"].Show(False)
            self.OptionsDialog["Buttons"]["Ok"].Show(True)
        
    #----------------------------
    # перерисовывает окно карты
    # подсвечивает открытые и закрытые уровни
    #----------------------------
    def _UpdateMapWindow(self):
        for i in range(self.TotalCareerLevels):
            tmpLevelFileName = "def/"+LevelStringName(i)+".def"
            tmpPlayerResult = defs.GetTagWithContent(globalvars.CurrentPlayerXML.GetTag(u"Levels"), u"level", tmpLevelFileName)
            if tmpPlayerResult.GetBoolAttr(u"expert"):
                self.MapCareerDialog["Buttons"]["Level_"+str(i)].SetButtonKlass(u"level-pointers-expert")
            else:
                self.MapCareerDialog["Buttons"]["Level_"+str(i)].SetButtonKlass(u"level-pointers")
            if tmpPlayerResult.GetBoolAttr(u"unlocked"):
                self.MapCareerDialog["Buttons"]["Level_"+str(i)].SetState(ButtonState_Up)
            else:
                self.MapCareerDialog["Buttons"]["Level_"+str(i)].SetState(ButtonState_Inert)
        if self.SelectedLevel >= 0:
            self.MapCareerDialog["Buttons"]["Start"].SetState(ButtonState_Up)
            self.MapCareerDialog["Buttons"]["Level_"+str(self.SelectedLevel)].SetState(ButtonState_Selected)
        else:
            self.MapCareerDialog["Buttons"]["Start"].SetState(ButtonState_Inert)
        
    def _CloseOptionsDialog(self, flag):
        if flag:
            globalvars.GameConfig["Fullscreen"] = self.OptionsDialog["Static"]["Galka_Fullscreen"].visible
            globalvars.GameConfig["Mute"] = self.OptionsDialog["Static"]["Galka_Mute"].visible
            globalvars.GameConfig["Hints"] = self.OptionsDialog["Static"]["Galka_Hints"].visible
        else:
            globalvars.GameConfig["Sound"] = self.SavedOptions["Sound"]
            globalvars.GameConfig["Music"] = self.SavedOptions["Music"]
        config.ApplyOptions()
        self._ReleaseState(PState_Options)
        
    def SendCommand(self, cmd):
        try:
            #developer logo
            if globalvars.StateStack[-1] == PState_DevLogo:
                if cmd == Cmd_DevLogoClose:
                    self._SetState(PState_PubLogo)
                
            #publisher logo
            elif globalvars.StateStack[-1] == PState_PubLogo:
                if cmd == Cmd_PubLogoClose:
                    self._SetState(PState_MainMenu)
                
            #main menu
            elif globalvars.StateStack[-1] == PState_MainMenu:
                if cmd == Cmd_Menu_PlayCareer:
                    #if globalvars.CurrentPlayer["Game"]:
                    #    self._AskYnc(Str_Question_Continue,
                    #        Str_Answer_Continue_Continue, Str_Answer_Continue_NewGame, Str_Cancel)
                    #else:
                        self._SetState(PState_MapCareer)
                elif cmd == Cmd_Menu_Players:
                    self._SetState(PState_Players)
                elif cmd == Cmd_Menu_Options:
                    self._SetState(PState_Options)
                elif cmd == Cmd_Menu_Rules:
                    self._SetState(PState_Help)
                elif cmd == Cmd_Menu_Hiscores:
                    self._SetState(PState_Hiscores)
                elif cmd == Cmd_Menu_Quit:
                    self._SetState(PState_EndGame)
                    
            #map window
            elif globalvars.StateStack[-1] == PState_MapCareer:
                if cmd == Cmd_MapStart:
                    self._ReleaseState(PState_MapCareer)
                    globalvars.CurrentPlayer["Level"] = "def/"+LevelStringName(self.SelectedLevel)+".def"
                    playerlist.ResetPlayer()
                    globalvars.CurrentPlayer["Playing"] = False
                    self._SetState(PState_Game)
                elif cmd == Cmd_MapMainMenu:
                    self._ReleaseState(PState_MapCareer)
                else:
                    self.SelectedLevel = cmd-Cmd_MapLevel
                    self._UpdateMapWindow()
                
            #rules dialog
            elif globalvars.StateStack[-1] == PState_Help:
                if cmd == Cmd_HelpPrev:
                    self._ShowHelpPage(self.CurrentHelpPage-1)
                elif cmd == Cmd_HelpNext:
                    self._ShowHelpPage(self.CurrentHelpPage+1)
                elif cmd == Cmd_HelpClose:
                    self._ReleaseState(PState_Help)    
                
            #players dialog
            elif globalvars.StateStack[-1] == PState_Players:
                if cmd == Cmd_PlayersRemove:
                    self._Ask(Str_Question_RemovePlayer)
                elif cmd == Cmd_PlayersOk:
                    if self.SelectedPlayer != -1:
                        tmpName = globalvars.PlList[self.SelectedPlayer]
                        globalvars.GameConfig["Player"] = tmpName
                        config.SaveGameConfig()
                        playerlist.ReadPlayer(tmpName)
                    self._ReleaseState(PState_Players)
                elif cmd == Cmd_PlayersCancel:
                    self.SelectedPlayer = -1
                    self._ReleaseState(PState_Players)
                elif cmd == Cmd_PlayersUp:
                    self.FirstPlayer -= 1
                    self._UpdatePlayersList()
                elif cmd == Cmd_PlayersDown:
                    self.FirstPlayer += 1
                    self._UpdatePlayersList()
                elif cmd in range(Cmd_PlayersSelect, \
                        Cmd_PlayersSelect+self.TotalPlayersOnScreen):
                    if cmd == Cmd_PlayersSelect and self.FirstPlayer == 0:
                        self._SetState(PState_EnterName)
                    else:
                        self.SelectedPlayer = self.FirstPlayer + cmd - Cmd_PlayersSelect
                        self._UpdatePlayersList()
            
            #options dialog
            elif globalvars.StateStack[-1] == PState_Options:
                if cmd == Cmd_OptionsOk:
                    self._CloseOptionsDialog(True)
                elif cmd == Cmd_OptionsCancel:
                    self._CloseOptionsDialog(False)
                elif cmd == Cmd_OptionsMute:
                    self.OptionsDialog["Static"]["Galka_Mute"].visible = not(self.OptionsDialog["Static"]["Galka_Mute"].visible)
                elif cmd == Cmd_OptionsHints:
                    self.OptionsDialog["Static"]["Galka_Hints"].visible = not(self.OptionsDialog["Static"]["Galka_Hints"].visible)
                elif cmd == Cmd_OptionsFullscreen:
                    self.OptionsDialog["Static"]["Galka_Fullscreen"].visible = not(self.OptionsDialog["Static"]["Galka_Fullscreen"].visible)
                elif cmd == Cmd_IGM_Resume:
                    self._CloseOptionsDialog(True)
                elif cmd == Cmd_IGM_Restart:
                    self._Ask(Str_Question_RestartLevel)
                elif cmd == Cmd_IGM_EndGame:
                    self._ReleaseState(PState_Options)
                    self._ReleaseState(PState_Game)
                    self._SetState(PState_MainMenu)    
                
            #hiscores dialog
            elif globalvars.StateStack[-1] == PState_Hiscores:
                if cmd == Cmd_HiscoresReset:
                    self._Ask(Str_Question_ClearHiscores)
                elif cmd == Cmd_HiscoresClose:
                    self._ReleaseState(PState_Hiscores)
            
            #entername dialog
            elif globalvars.StateStack[-1] == PState_EnterName:
                if cmd == Cmd_EnterNameOk:
                    tmpName = self.EnterNameDialog["Text"]["Name"].text
                    if len(tmpName) == 0:
                        self.EnterNameDialog["Text"]["NameErrors"].text = Str_EnterName_Error_Empty
                        return
                    elif tmpName == 'None':
                        self.EnterNameDialog["Text"]["NameErrors"].text = Str_EnterName_Error_Bad
                        return
                    elif globalvars.PlList.count(tmpName) > 0:
                        self.EnterNameDialog["Text"]["NameErrors"].text = Str_EnterName_Error_Exist
                        return
                    else:
                        playerlist.NewPlayer(tmpName)
                        self.SelectedPlayer = len(globalvars.PlList) - 1 
                        self._DrawPlayersList()
                elif cmd == Cmd_EnterNameCancel:
                    pass
                self.EnterNameDialog["Text"]["Name"].text = u""
                self.EnterNameDialog["Static"]["TextCursor"].x = self.EnterNameDialog["Text"]["Name"].x
                self._ReleaseState(PState_EnterName)
            
            #yes-no dialog
            elif globalvars.StateStack[-1] == PState_YesNo:
                self._ReleaseState(PState_YesNo)
                if cmd == Cmd_Yes:
                    #remove player
                    if globalvars.StateStack[-1] == PState_Players:
                        playerlist.DelPlayer(globalvars.PlList[self.SelectedPlayer])
                        self.SelectedPlayer = -1
                        self._DrawPlayersList()
                    #clear hiscores
                    elif globalvars.StateStack[-1] == PState_Hiscores:
                        config.ClearHiscores()
                    #restart game
                    elif globalvars.StateStack[-1] == PState_Options:
                        self._ReleaseState(PState_Options)
                        globalvars.Board.Restart()
                    
            elif globalvars.StateStack[-1] == PState_YesNoCancel:
                self._ReleaseState(PState_YesNoCancel)
                if cmd == Cmd_YncYes:
                    #continue game
                    if globalvars.StateStack[-1] == PState_MainMenu:
                        self._SetState(PState_Game)
                elif cmd == Cmd_YncNo:
                    #start new game
                    if globalvars.StateStack[-1] == PState_MainMenu:
                        globalvars.CurrentPlayer["Game"] = False
                        globalvars.CurrentPlayer["Playing"] = False
                        self._SetState(PState_MapCareer)
                elif cmd == Cmd_YncCancel:
                    pass
                    
            #level complete dialog
            elif globalvars.StateStack[-1] == PState_NextLevel:
                self._ReleaseState(PState_NextLevel)
                if cmd == Cmd_LvCompleteNextLevel:
                    tmpLevel = globalvars.CurrentPlayer["Level"]
                    if levels.Levels[tmpLevel]["NoInEpisode"] == 0 and self.LvCompleteSuccess:
                        self._SetState(PState_EpiComplete)
                    else:
                        self._SetState(PState_Game)
                elif cmd == Cmd_LvCompleteMainMenu:
                    self._ReleaseState(PState_Game)
                
            #episode complete dialog
            elif globalvars.StateStack[-1] == PState_EpiComplete:
                self._ReleaseState(PState_EpiComplete)
                if cmd == Cmd_EpiCompleteNext:
                    self._SetState(PState_Game)
                elif cmd == Cmd_EpiCompleteMainMenu:
                    self._ReleaseState(PState_Game)
            
            #end game dialog
            elif globalvars.StateStack[-1] == PState_GameOver:
                self._ReleaseState(PState_GameOver)
                self._ReleaseState(PState_Game)
                if cmd == Cmd_GameOverHiscores:
                    self._SetState(PState_Hiscores)
                elif cmd == Cmd_GameOverMainMenu:
                    self._SetState(PState_MainMenu)
                self._ReleaseState(PState_Game)
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        
    def _OnExecute(self, que) :
        #показываем логотипы разработчика и паблишера
        if globalvars.StateStack[-1] == PState_DevLogo:
            self.NextStateTime -= que.delta
            if self.NextStateTime <= 0:
                self.SendCommand(Cmd_DevLogoClose)
        if globalvars.StateStack[-1] == PState_PubLogo:
            self.NextStateTime -= que.delta
            if self.NextStateTime <= 0:
                self.SendCommand(Cmd_PubLogoClose)
            
        #обрабатываем ввод имени игрока с клавиатуры
        if globalvars.StateStack[-1] == PState_EnterName:
            if oE.EvtIsKeyDown():
                self.EnterNameDialog["Text"]["NameErrors"].text = u""
                tmpName = self.EnterNameDialog["Text"]["Name"].text
                if scraft.Key_A <= oE.EvtKey() <= scraft.Key_Z:
                    tmpLetter = Const_AllChars[oE.EvtKey() - scraft.Key_A]
                    if oE.IsKeyPressed(scraft.Key_SHIFT) or oE.IsKeyPressed(scraft.Key_RSHIFT):
                        pass
                    else:
                        tmpLetter = string.lower(tmpLetter)
                    tmpName += tmpLetter
                elif scraft.Key_0 <= oE.EvtKey() <= scraft.Key_9:
                    tmpName += str(oE.EvtKey() - scraft.Key_0)
                elif oE.EvtKey() == scraft.Key_SPACE:
                    tmpName += " "
                elif oE.EvtKey() == scraft.Key_BACKSPACE:
                    tmpName = tmpName[0:len(tmpName)-1]
                elif oE.EvtKey() == scraft.Key_ESC:
                    self.SendCommand(Cmd_EnterNameCancel)
                elif oE.EvtKey() == scraft.Key_ENTER:
                    self.SendCommand(Cmd_EnterNameOk)
                if len(tmpName) > Max_NameLen:
                    tmpName = tmpName[0:len(tmpName)-1]
                self.EnterNameDialog["Text"]["Name"].text = unicode(tmpName)
                self.EnterNameDialog["Static"]["TextCursor"].x = self.EnterNameDialog["Text"]["Name"].x + \
                    self.EnterNameDialog["Text"]["Name"].width/2
            
        if oE.EvtIsESC():
            if globalvars.StateStack[-1] == PState_DevLogo:
                self.SendCommand(Cmd_DevLogoClose)
            elif globalvars.StateStack[-1] == PState_PubLogo:
                self.SendCommand(Cmd_PubLogoClose)
            elif globalvars.StateStack[-1] == PState_MainMenu:    
                self._SetState(PState_EndGame)
            elif globalvars.StateStack[-1] == PState_Game:
                self.CallInternalMenu()
            elif globalvars.StateStack[-1] == PState_Help:
                self.SendCommand(Cmd_HelpClose)
            elif globalvars.StateStack[-1] == PState_Options:
                self._CloseOptionsDialog(False)
            elif globalvars.StateStack[-1] == PState_YesNo:
                self.SendCommand(Cmd_No)
            elif globalvars.StateStack[-1] == PState_YesNoCancel:
                self.SendCommand(Cmd_YncCancel)
            elif globalvars.StateStack[-1] == PState_Hiscores:
                self.SendCommand(Cmd_HiscoresClose)
            elif globalvars.StateStack[-1] == PState_Players:
                self.SendCommand(Cmd_PlayersCancel)
            elif globalvars.StateStack[-1] == PState_MapCareer:
                self.SendCommand(Cmd_MapMainMenu)
            elif globalvars.StateStack[-1] == PState_EnterName:
                self.SendCommand(Cmd_EnterNameCancel)
            elif globalvars.StateStack[-1] == PState_NextLevel:
                self.SendCommand(Cmd_LvCompleteMainMenu)
            elif globalvars.StateStack[-1] == PState_GameOver:
                self.SendCommand(Cmd_GameOverMainMenu)
        
        if oE.EvtIsQuit():
            if globalvars.StateStack[-1] in (PState_MainMenu, PState_Help, PState_Options,
                    PState_InGameMenu, PState_Hiscores, PState_Players,
                    PState_MapCareer, PState_YesNo, PState_EnterName, PState_NextLevel, PState_GameOver):    
                self._SetState(PState_EndGame)
            elif globalvars.StateStack[-1] == PState_Game:
                self._SetState(PState_Options)
            
        return scraft.CommandStateRepeat
        
    def _ReleaseState(self, state):
        if state == PState_DevLogo:
            self._ShowDialog(self.DevLogo, False)
        elif state == PState_PubLogo:
            self._ShowDialog(self.PubLogo, False)
        elif state == PState_MainMenu:
            self._ShowDialog(self.MainMenuDialog, False)
        elif state == PState_MapCareer:
            self._ShowDialog(self.MapCareerDialog, False)
        elif state == PState_NextLevel:
            self._ShowDialog(self.LevelCompleteDialog, False)
        elif state == PState_EpiComplete:
            self._ShowDialog(self.EpisodeCompleteDialog, False)
        elif state == PState_GameOver:
            self._ShowDialog(self.GameOverDialog, False)
        elif state == PState_Players:
            self._ShowDialog(self.PlayersDialog, False)
        elif state == PState_EnterName:
            self._ShowDialog(self.EnterNameDialog, False)
        elif state == PState_Help:
            self._ShowDialog(self.RulesDialog, False)
        elif state == PState_Hiscores:
            self._ShowDialog(self.HiscoresDialog, False)
        elif state == PState_Options:
            self._ShowDialog(self.OptionsDialog, False)
        elif state == PState_YesNo:
            self._ShowDialog(self.YesNoDialog, False)
        elif state == PState_YesNoCancel:
            self._ShowDialog(self.YesNoCancelDialog, False)
        elif state == PState_Game:
            globalvars.Board.Show(False)
            #globalvars.ActiveGameSession
        if globalvars.StateStack != [] and globalvars.StateStack[-1] == state:
            globalvars.StateStack.pop()
            if len(globalvars.StateStack)>0:
                self._SetState(globalvars.StateStack[-1])
        
    # запуск указанного уровня
    def JustRun(self):
        playerlist.ResetPlayer()
        globalvars.CurrentPlayer["Playing"] = False
        self._SetState(PState_Game)
        
        
    def _SetState(self, state):
        if globalvars.StateStack == [] or globalvars.StateStack[-1] != state:
            globalvars.StateStack.append(state)
        if state in (PState_Game, PState_InGameMenu, PState_NextLevel,
                     PState_EpiComplete, PState_GameOver):
            globalvars.Musician.SetState(MusicState_Game)
        else:
            globalvars.Musician.SetState(MusicState_Menu)
        if state == PState_Game:
            self._ReleaseState(PState_MainMenu)
            self._ReleaseState(PState_MapCareer)
            self._ReleaseState(PState_PubLogo)
            self._ReleaseState(PState_DevLogo)
            
            #globalvars.Board.Show(True)
            #globalvars.Board.LaunchLevel(globalvars.CurrentPlayer["Level"])
            
            if globalvars.ActiveGameSession == True:
                globalvars.Board.Freeze(False)
            #elif globalvars.CurrentPlayer["Playing"] == True:
            #    globalvars.Board.Show(True)
            #    globalvars.Board.LoadGame()
            else:
                globalvars.Board.Show(True)
                globalvars.Board.LaunchLevel(globalvars.CurrentPlayer["Level"])
                #if globalvars.CurrentPlayer["Game"]:
                #    globalvars.Board.Show(True)
                #    if globalvars.CurrentPlayer["Level"] == 0 and self.LvCompleteSuccess:
                #        playerlist.ResetPlayer()
                #    globalvars.Board.LaunchLevel(globalvars.CurrentPlayer["Level"])
            #    #else:
            #    #    self._SetState(PState_MapCareer)
        elif state == PState_DevLogo:
            self._ShowDialog(self.DevLogo, True)
            self._ReleaseState(PState_PubLogo)
            self._ReleaseState(PState_MainMenu)
            self._ReleaseState(PState_Players)
            self._ReleaseState(PState_EnterName)
            self._ReleaseState(PState_Help)
            self._ReleaseState(PState_Options)
            self._ReleaseState(PState_Hiscores)
            self._ReleaseState(PState_YesNo)
            self._ReleaseState(PState_YesNoCancel)
            self._ReleaseState(PState_NextLevel)
            self._ReleaseState(PState_EpiComplete)
            self._ReleaseState(PState_GameOver)
            self._ReleaseState(PState_MapCareer)
            self.NextStateTime = Time_DevLogoShow
            
        elif state == PState_PubLogo:
            self._ShowDialog(self.PubLogo, True)
            self._ReleaseState(PState_DevLogo)
            self.NextStateTime = Time_PubLogoShow
            
        elif state == PState_MainMenu:
            self._ShowDialog(self.MainMenuDialog, True)
            self._ReleaseState(PState_PubLogo)
            self._ReleaseState(PState_Players)
            self._ReleaseState(PState_EnterName)
            self._ReleaseState(PState_Help)
            self._ReleaseState(PState_Options)
            self._ReleaseState(PState_Hiscores)
            self._ReleaseState(PState_YesNo)
            self._ReleaseState(PState_YesNoCancel)
            self._ReleaseState(PState_NextLevel)
            self._ReleaseState(PState_EpiComplete)
            self._ReleaseState(PState_GameOver)
            self._ReleaseState(PState_MapCareer)
            if globalvars.GameConfig["Player"] == 'None' or \
                globalvars.PlList.count(globalvars.GameConfig["Player"]) == 0:
                self.MainMenuDialog["Text"]["WelcomeMessage"].visible = False
                self.MainMenuDialog["Buttons"]["Players"].Show(False)
                #self.MainMenuDialog["Text"]["WelcomeMessage"].text = u"" #u"Welcome, guest"
                if len(globalvars.PlList) <= 1:
                    self._SetState(PState_EnterName)
                else:
                    self._SetState(PState_Players)
            else:
                self.MainMenuDialog["Text"]["WelcomeMessage"].visible = True
                self.MainMenuDialog["Buttons"]["Players"].Show(True)
                self.MainMenuDialog["Text"]["WelcomeMessage"].text = Str_Menu_Welcome + globalvars.GameConfig["Player"]
            
        elif state == PState_MapCareer:
            self._ReleaseState(PState_MainMenu)
            self.SelectedLevel = -1
            self._ShowDialog(self.MapCareerDialog, True)
            self._UpdateMapWindow()
            
        elif state == PState_NextLevel:
            globalvars.Board.Freeze(True)
            self._ShowDialog(self.LevelCompleteDialog, True)
            
        elif state == PState_EpiComplete:
            self._ShowDialog(self.EpisodeCompleteDialog, True)
            
        elif state == PState_GameOver:
            globalvars.Board.Freeze(True)
            self._ShowDialog(self.GameOverDialog, True)
            
        elif state == PState_Players:
            self._ShowDialog(self.PlayersDialog, True)
            self._DrawPlayersList()
            
        elif state == PState_EnterName:
            self._ShowDialog(self.EnterNameDialog, True)
            
        elif state == PState_Help:
            self._ReleaseState(PState_MainMenu)
            self._ShowDialog(self.RulesDialog, True)
            self._ShowHelpPage(self.CurrentHelpPage)
            
        elif state == PState_Hiscores:
            self._ShowDialog(self.MainMenuDialog, True)
            config.UpdateHiscores()
            self._ShowDialog(self.HiscoresDialog, True)
            self._UpdateHiscoresDialog()
            
        elif state == PState_Options:
            globalvars.Board.Freeze(True)
            self.SavedOptions = dict(globalvars.GameConfig)
            self._ShowDialog(self.OptionsDialog, True)
            self._UpdateOptionsDialog()
            
        elif state == PState_YesNo:
            self._ShowDialog(self.YesNoDialog, True)
            
        elif state == PState_YesNoCancel:
            self._ShowDialog(self.YesNoCancelDialog, True)
            
        elif state == PState_EndGame:
            pass
        
        
def LevelStringName(no):
    if no >= 10:
        return str(no)
    else:
        return "0"+str(no)


