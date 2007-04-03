#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Project: Master Chef
������ �������� ��� ������������ ����
"""

import scraft

#������ ����
FieldMinX = 0
FieldMinY = 0
FieldMaxX = 800
FieldMaxY = 600
Crd_deltaX = Crd_deltaY = 40
Video_Mode = scraft.VMODE_800x600x32
Window_Title = u"Master Chef"

#����� ������
File_GameConfig = u"data/game.def"
File_Hiscores = u"data/scores.def"
File_BestResults = u"data/best.def"
File_PlayersConfig = u"data/players.def"

File_PlayersConfigSafe = u"safe/players.def"
File_DummyProfile = u"safe/dummy.def"
File_GameConfigSafe = u"safe/game.def"
File_BestResultsSafe = u"safe/best.def"

File_SST = u"masterchef.sst"

File_Cuisine = u"def/cuisine.def"
File_GameSettings = u"def/gamesettings.def"
File_ResourceInfo = u"def/resource.def"
File_Animations = u"def/animations.def"
File_LevelProgress = u"def/levelprogress.def"

#���������
Str_SignatureBegin = "signature{\n  value("
Str_SignatureEnd = ")\n}\n"

# ��������� ��������� ������
NewGame_Score = 0
NewLevel_Score = 0

RunMode_Test = 0
RunMode_Play = 1

