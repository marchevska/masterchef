@echo off

REM ***************
REM english version
REM ***************

cd %~dp0
call "abc english.bat"

REM build full version
copy .\def\levelprogress.full.def .\def\levelprogress.def
copy .\safe\dummy.full.def .\safe\dummy.def

REM **** no branding ****
cd %~dp0
copy .\branding\none\branding.def .\def\branding.def
copy .\branding\none\publisher-logo.png .\img\logos\publisher-logo.png
"C:\Program Files\MoleBoxPro\mbox2c.exe" main.exe
cd ..
ren "%cd%\release\def.dat" "def.full.dat"
move "%cd%\release\*.*" "%cd%\release\english full\"
cd ".\release\english full\"
"c:\Projects\Jungle\zip.exe" "..\zip\ChampionChefReleaseEn.zip" "*.*"
copy "*.*" "..\english full for iWin\ChampionChef\nonbranded\"

REM **** BFG branding ****
cd %~dp0
copy .\branding\bfg\branding.def .\def\branding.def
"C:\Program Files\MoleBoxPro\mbox2c.exe" main.exe
cd ..
copy "%cd%\current\branding\bfg\splash_forWhiteBg_800x600.png" "%cd%\release\english full for BFG\splash_forWhiteBg_800x600.png"
copy "%cd%\current\branding\bfg\bfglogo_150x125.png" "%cd%\release\english full for BFG\bfglogo_150x125.png"
ren "%cd%\release\def.dat" "def.full.dat"
move "%cd%\release\*.*" "%cd%\release\english full for BFG\"
cd ".\release\english full for BFG\"
"c:\Projects\Jungle\zip.exe" "..\zip\english full for BFG\ChampionChef_Teggo.zip" "*.*"

REM **** iWin branding ****
cd %~dp0
copy .\branding\iwin\branding.def .\def\branding.def
"C:\Program Files\MoleBoxPro\mbox2c.exe" main.exe
cd ..
copy "%cd%\current\branding\iwin\splash-iwin_com_logo-withDotCom.PNG" "%cd%\release\english full for iWin\ChampionChef\executable\splash-iwin_com_logo-withDotCom.PNG"
copy "%cd%\current\branding\iwin\iWin_logo_small-150px-flat-RGB.PNG" "%cd%\release\english full for iWin\ChampionChef\executable\iWin_logo_small-150px-flat-RGB.PNG"
ren "%cd%\release\def.dat" "def.full.dat"
move "%cd%\release\*.*" "%cd%\release\english full for iWin\ChampionChef\executable\"
cd ".\release\english full for iWin\"
"c:\Projects\Jungle\zip.exe" -r "..\zip\english full for iWin\ChampionChef.zip" "*.*"

REM build demo version
cd %~dp0
copy .\def\levelprogress.demo.def .\def\levelprogress.def
copy .\safe\dummy.demo.def .\safe\dummy.def
copy .\branding\none\branding.def .\def\branding.def
copy .\branding\none\publisher-logo.png .\img\logos\publisher-logo.png
"C:\Program Files\MoleBoxPro\mbox2c.exe" main.exe
cd ..
ren "%cd%\release\def.dat" "def.demo.dat"
ren "%cd%\release\ChampionChefReleaseEn.exe" "ChampionChefDemoEn.exe"
move "%cd%\release\*.*" "%cd%\release\english demo\"
cd ".\release\english demo\"
"c:\Projects\Jungle\zip.exe" "..\zip\ChampionChefDemoEn.zip" "*.*"

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


