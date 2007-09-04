@echo off

REM build full version
cd %~dp0
copy .\def\levelprogress.full.def .\def\levelprogress.def
copy .\safe\dummy.full.def .\safe\dummy.def
"C:\Program Files\MoleBoxPro\mbox2c.exe" main.exe
cd ..
copy "%cd%\release\def.dat" "%cd%\release\def.full.dat"
del "%cd%\release\def.dat"

@REM build demo version
cd %~dp0
copy .\def\levelprogress.demo.def .\def\levelprogress.def
copy .\safe\dummy.demo.def .\safe\dummy.def
"C:\Program Files\MoleBoxPro\mbox2c.exe" main.exe
cd ..
copy "%cd%\release\def.dat" "%cd%\release\def.demo.dat"
del "%cd%\release\def.dat"

@REM restore to the previous state version
cd %~dp0
copy .\def\levelprogress.full.def .\def\levelprogress.def
copy .\safe\dummy.full.def .\safe\dummy.def


