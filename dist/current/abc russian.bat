@echo off

cd %~dp0
copy "%cd%\abc russian\def\*.def" "%cd%\def\*.def"
copy "%cd%\abc russian\img\comics\*.png" "%cd%\img\comics\*.png"
copy "%cd%\abc russian\img\cookbook\*.png" "%cd%\img\cookbook\*.png"
copy "%cd%\abc russian\img\cookbook\american\*.png" "%cd%\img\cookbook\american\*.png"
copy "%cd%\abc russian\img\cookbook\hawaiian\*.png" "%cd%\img\cookbook\hawaiian\*.png"
copy "%cd%\abc russian\img\cookbook\japanese\*.png" "%cd%\img\cookbook\japanese\*.png"
copy "%cd%\abc russian\img\cookbook\mexican\*.png" "%cd%\img\cookbook\mexican\*.png"
copy "%cd%\abc russian\img\cookbook\russian\*.png" "%cd%\img\cookbook\russian\*.png"
copy "%cd%\abc russian\img\fonts\*.png" "%cd%\img\fonts\*.png"
copy "%cd%\abc russian\img\gui\*.png" "%cd%\img\gui\*.png"

