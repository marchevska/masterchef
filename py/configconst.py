#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Project: Master Chef
Список констант для конфигурации игры
"""

import scraft

#размер поля
FieldMinX = 0
FieldMinY = 0
FieldMaxX = 800
FieldMaxY = 600
Crd_deltaX = Crd_deltaY = 40
Video_Mode = scraft.VMODE_800x600x32
Window_Title = u"Master Chef"

#имена файлов
File_GameSave = u"data/game.sav"
File_GameConfig = u"data/game.def"
File_GameConfigSafe = u"safe/game.def"
File_Hiscores = u"data/scores.def"
File_BestResults = u"data/best.def"
File_PlayersConfig = u"data/players.def"
File_DummyProfile = u"safe/dummy.def"
File_SST = u"masterchef.sst"

File_Cuisine = u"def/cuisine.def"
File_GameSettings = u"def/gamesettings.def"
File_ResourceInfo = u"def/resource.def"
File_Animations = u"def/animations.def"
File_LevelProgress = u"def/levelprogress.def"

#сигнатура
Str_SignatureBegin = "signature{\n  value("
Str_SignatureEnd = ")\n}\n"

# стартовые параметры игрока
NewGame_Score = 0
NewLevel_Score = 0
