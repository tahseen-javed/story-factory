@echo off
rem Drag your music/SFX .zip onto this file. It encrypts it with the factory's PUBLIC age key so it can be uploaded to a public Release.
set AGE=%USERPROFILE%\.story-factory\age.exe
set RECIPIENT=age1a29zkhm3egxk30kdylsygf6pdkvkk2j6dz4h5qqacvga8ezf550qwl54rq
if "%~1"=="" (echo Drag a .zip file onto this script. & pause & exit /b 1)
"%AGE%" -r %RECIPIENT% -o "%~1.age" "%~1"
echo Created "%~1.age" - upload that file to the GitHub release library-music-v1. Then delete the original zip.
pause
