@echo off

REM ***************
REM english version
REM ***************

cd %~dp0
call "abc english.bat"

REM build full version
copy .\def\levelprogress.full.def .\def\levelprogress.def
copy .\safe\dummy.full.def .\safe\dummy.def
"C:\Program Files\MoleBoxPro\mbox2c.exe" main.exe
cd ..
ren "%cd%\release\def.dat" "def.full.dat"

move "%cd%\release\*.*" "%cd%\release\english full\"


REM build demo version
cd %~dp0
copy .\def\levelprogress.demo.def .\def\levelprogress.def
copy .\safe\dummy.demo.def .\safe\dummy.def
"C:\Program Files\MoleBoxPro\mbox2c.exe" main.exe
cd ..
ren "%cd%\release\def.dat" "def.demo.dat"
ren "%cd%\release\ChampionChefReleaseEn.exe" "ChampionChefDemoEn.exe"

move "%cd%\release\*.*" "%cd%\release\english demo\"


REM restore to the previous state version
cd %~dp0
copy .\def\levelprogress.full.def .\def\levelprogress.def
copy .\safe\dummy.full.def .\safe\dummy.def


REM ***************
REM russian version
REM ***************

cd %~dp0
call "abc russian.bat"

REM build full version
copy .\def\levelprogress.full.def .\def\levelprogress.def
copy .\safe\dummy.full.def .\safe\dummy.def
"C:\Program Files\MoleBoxPro\mbox2c.exe" main.exe
cd ..
ren "%cd%\release\def.dat" "def.full.dat"
ren "%cd%\release\ChampionChefReleaseEn.exe" "ChampionChefReleaseRu.exe"

move "%cd%\release\*.*" "%cd%\release\russian full\"


@REM build demo version
cd %~dp0
copy .\def\levelprogress.demo.def .\def\levelprogress.def
copy .\safe\dummy.demo.def .\safe\dummy.def
"C:\Program Files\MoleBoxPro\mbox2c.exe" main.exe
cd ..
ren "%cd%\release\def.dat" "def.demo.dat"
ren "%cd%\release\ChampionChefReleaseEn.exe" "ChampionChefDemoRu.exe"

move "%cd%\release\*.*" "%cd%\release\russian demo\"


@REM restore to the previous state version
cd %~dp0
copy .\def\levelprogress.full.def .\def\levelprogress.def
copy .\safe\dummy.full.def .\safe\dummy.def
call "abc english.bat"


