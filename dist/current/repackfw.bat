@echo off

cd %~dp0
cd "..\..\..\..\1\py\"
call "_compile.bat"

cd %~dp0
"C:\Projects\Jungle\a+.exe" "main.exe.config"

REM **** FULL * ENG * TEGGO branding ****
cd %~dp0
copy main.exe "..\release\_fw english full\ChampionChefReleaseEn.exe"
copy pyteggo2.dll "..\release\_fw english full\"
copy scraft.dll "..\release\_fw english full\"
cd ..
cd "release"
copy "_fw_temp\def.dat" "_fw english full\def.dat"
copy "_fw_temp\def.full.dat" "_fw english full\def.full.dat"
copy "_fw_temp\ide.teggo.dat" "_fw english full\ide.teggo.dat"
copy "_fw_temp\img.dat" "_fw english full\img.dat"
copy "_fw_temp\lang.eng.dat" "_fw english full\lang.eng.dat"
copy "_fw_temp\levels.dat" "_fw english full\levels.dat"
copy "_fw_temp\snd.dat" "_fw english full\snd.dat"
cd "_fw english full"
"c:\Projects\Jungle\zip.exe" -r0 "..\_fw_zip\ChampionChefReleaseEn.zip" "*.*"


REM **** FULL * ENG * BFG branding ****
cd %~dp0
copy main.exe "..\release\_fw english full for BFG\ChampionChef.exe"
copy pyteggo2.dll "..\release\_fw english full for BFG\"
copy scraft.dll "..\release\_fw english full for BFG\"
cd ..
copy "current\branding\bfg\splash_forWhiteBg_800x600.png" "release\_fw english full for BFG\"
copy "current\branding\bfg\bfglogo_150x125.png" "release\_fw english full for BFG\"
cd "release"
copy "_fw_temp\def.dat" "_fw english full for BFG\def.dat"
copy "_fw_temp\def.full.dat" "_fw english full for BFG\def.full.dat"
copy "_fw_temp\ide.bfg.dat" "_fw english full for BFG\ide.bfg.dat"
copy "_fw_temp\img.dat" "_fw english full for BFG\img.dat"
copy "_fw_temp\lang.eng.dat" "_fw english full for BFG\lang.eng.dat"
copy "_fw_temp\levels.dat" "_fw english full for BFG\levels.dat"
copy "_fw_temp\snd.dat" "_fw english full for BFG\snd.dat"
cd "_fw english full for BFG"
"c:\Projects\Jungle\zip.exe" -r0 "..\_fw_zip\english full for BFG\ChampionChef_Teggo.zip" "*.*"


REM **** FULL * ENG * IWIN branding ****
cd %~dp0
copy main.exe "..\release\_fw english full for iWin\ChampionChef\executable\ChampionChef.exe"
copy pyteggo2.dll "..\release\_fw english full for iWin\ChampionChef\executable\"
copy scraft.dll "..\release\_fw english full for iWin\ChampionChef\executable\"
cd ..
copy "current\branding\iwin\splash-iwin_com_logo-withDotCom.png" "release\_fw english full for iWin\ChampionChef\executable\"
copy "current\branding\iwin\iWin_logo_small-150px-flat-RGB.png" "release\_fw english full for iWin\ChampionChef\executable\"
cd "release"
copy "_fw_temp\def.dat" "_fw english full for iWin\ChampionChef\executable\def.dat"
copy "_fw_temp\def.full.dat" "_fw english full for iWin\ChampionChef\executable\def.full.dat"
copy "_fw_temp\ide.iwin.dat" "_fw english full for iWin\ChampionChef\executable\ide.iwin.dat"
copy "_fw_temp\img.dat" "_fw english full for iWin\ChampionChef\executable\img.dat"
copy "_fw_temp\lang.eng.dat" "_fw english full for iWin\ChampionChef\executable\lang.eng.dat"
copy "_fw_temp\levels.dat" "_fw english full for iWin\ChampionChef\executable\levels.dat"
copy "_fw_temp\snd.dat" "_fw english full for iWin\ChampionChef\executable\snd.dat"

REM **** FULL * ENG * TEGGO branding for iWin ****
copy "_fw english full\*.*" "_fw english full for iWin\ChampionChef\nonbranded"
cd "_fw english full for iWin"
"c:\Projects\Jungle\zip.exe" -r0 "..\_fw_zip\english full for iWin\ChampionChef.zip" "*.*"


REM **** DEMO * ENG * TEGGO branding ****
cd %~dp0
copy main.exe "..\release\_fw english demo\ChampionChefDemoEn.exe"
copy pyteggo2.dll "..\release\_fw english demo\"
copy scraft.dll "..\release\_fw english demo\"
cd ..
cd "release"
copy "_fw_temp\def.dat" "_fw english demo\def.dat"
copy "_fw_temp\def.demo.dat" "_fw english demo\def.demo.dat"
copy "_fw_temp\ide.teggo.dat" "_fw english demo\ide.teggo.dat"
copy "_fw_temp\img.dat" "_fw english demo\img.dat"
copy "_fw_temp\lang.eng.dat" "_fw english demo\lang.eng.dat"
copy "_fw_temp\levels.dat" "_fw english demo\levels.dat"
copy "_fw_temp\snd.dat" "_fw english demo\snd.dat"
cd "_fw english demo"
"c:\Projects\Jungle\zip.exe" -r0 "..\_fw_zip\ChampionChefDemoEn.zip" "*.*"


REM **** FULL * RUS * TEGGO branding ****
cd %~dp0
copy main.exe "..\release\_fw russian full\ChampionChefReleaseRu.exe"
copy pyteggo2.dll "..\release\_fw russian full\"
copy scraft.dll "..\release\_fw russian full\"
cd ..
cd "release"
copy "_fw_temp\def.dat" "_fw russian full\def.dat"
copy "_fw_temp\def.full.dat" "_fw russian full\def.full.dat"
copy "_fw_temp\ide.teggo.dat" "_fw russian full\ide.teggo.dat"
copy "_fw_temp\img.dat" "_fw russian full\img.dat"
copy "_fw_temp\lang.rus.dat" "_fw russian full\lang.rus.dat"
copy "_fw_temp\levels.dat" "_fw russian full\levels.dat"
copy "_fw_temp\snd.dat" "_fw russian full\snd.dat"
cd "_fw russian full"
"c:\Projects\Jungle\zip.exe" -r0 "..\_fw_zip\ChampionChefReleaseRu.zip" "*.*"


REM **** FULL * RUS * NEVOSOFT branding ****
cd %~dp0
copy main.exe "..\release\_fw russian full for Nevosoft\ChampionChefReleaseRu.exe"
copy pyteggo2.dll "..\release\_fw russian full for Nevosoft\"
copy scraft.dll "..\release\_fw russian full for Nevosoft\"
cd ..
copy "current\branding\nevosoft ru\splash1.jpg" "release\_fw russian full for Nevosoft\"
cd "release"
copy "_fw_temp\def.dat" "_fw russian full for Nevosoft\def.dat"
copy "_fw_temp\def.full.dat" "_fw russian full for Nevosoft\def.full.dat"
copy "_fw_temp\ide.nevosoft.dat" "_fw russian full for Nevosoft\ide.nevosoft.dat"
copy "_fw_temp\img.dat" "_fw russian full for Nevosoft\img.dat"
copy "_fw_temp\lang.rus.dat" "_fw russian full for Nevosoft\lang.rus.dat"
copy "_fw_temp\levels.dat" "_fw russian full for Nevosoft\levels.dat"
copy "_fw_temp\snd.dat" "_fw russian full for Nevosoft\snd.dat"
cd "_fw russian full for Nevosoft"
"c:\Projects\Jungle\zip.exe" -r0 "..\_fw_zip\russian full for Nevosoft\ChampionChef.zip" "*.*"


REM **** DEMO * RUS * TEGGO branding ****
cd %~dp0
copy main.exe "..\release\_fw russian demo\ChampionChefDemoRu.exe"
copy pyteggo2.dll "..\release\_fw russian demo\"
copy scraft.dll "..\release\_fw russian demo\"
cd ..
cd "release"
copy "_fw_temp\def.dat" "_fw russian demo\def.dat"
copy "_fw_temp\def.demo.dat" "_fw russian demo\def.demo.dat"
copy "_fw_temp\ide.teggo.dat" "_fw russian demo\ide.teggo.dat"
copy "_fw_temp\img.dat" "_fw russian demo\img.dat"
copy "_fw_temp\lang.rus.dat" "_fw russian demo\lang.rus.dat"
copy "_fw_temp\levels.dat" "_fw russian demo\levels.dat"
copy "_fw_temp\snd.dat" "_fw russian demo\snd.dat"
cd "_fw russian demo"
"c:\Projects\Jungle\zip.exe" -r0 "..\_fw_zip\ChampionChefDemoRu.zip" "*.*"

