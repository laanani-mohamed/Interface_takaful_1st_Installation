@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: Construire les chemins sans backslash final
set "BASEDIR=%~dp0"
set "BASEDIR=!BASEDIR:~0,-1!"
set "PYTHON=!BASEDIR!\python_portable\python.exe"
set "GET_PIP=!BASEDIR!\python_portable\get-pip.py"

:: 1 - Verifier que python.exe existe
if not exist "!PYTHON!" (
    echo ERREUR : python.exe introuvable dans python_portable\
    pause
    exit /b 1
)

:: 2 - Installer pip si absent
"!PYTHON!" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Pip absent - installation via get-pip.py ...
    if not exist "!GET_PIP!" (
        echo ERREUR : get-pip.py introuvable dans python_portable\
        pause
        exit /b 1
    )
    "!PYTHON!" "!GET_PIP!"
) else (
    echo Pip deja present.
)

:: 3 - Activer les imports (fix Python embeddable)
echo import site > "!BASEDIR!\python_portable\sitecustomize.py"

:: 4 - Installer tous les wheels locaux
::     On se place dans le dossier Scripts (pushd)
::     et on passe le chemin relatif ./fichier.whl
set "WHEEL_FOUND=0"
pushd "!BASEDIR!"
for %%F in (*.whl) do (
    set "WHEEL_FOUND=1"
    echo Installation : %%F
    "!PYTHON!" -m pip install --no-index "./%%F"
)
popd

if "!WHEEL_FOUND!"=="0" (
    echo Aucun fichier .whl trouve - verifiez le dossier Scripts.
)

:: 5 - Installer depuis requirements.txt
if exist "!BASEDIR!\requirements.txt" (
    echo Installation depuis requirements.txt ...
    "!PYTHON!" -m pip install --no-index --find-links="!BASEDIR!" -r "!BASEDIR!\requirements.txt"
) else (
    echo requirements.txt absent - etape ignoree.
)

:: 6 - Lancer le script principal
echo.
echo ==============================
echo  Lancement de Interface_Takaful.py
echo ==============================
"!PYTHON!" "!BASEDIR!\Interface_Takaful.py"
pause
endlocal
