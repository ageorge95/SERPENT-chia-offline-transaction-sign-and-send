@echo off

set python=%1
IF "%python%"=="" set python="python"

set root=%cd%

:: installation

git submodule update --progress --init --recursive --force

%python% -m venv venv
:: Windows doesn't allow the creation of symlinks without special priviledges, so hardlinks are created instead.
mklink /h activate.bat venv\Scripts\activate.bat
mklink /j venv\Scripts\chia chia_blockchain\chia
mklink /j chia chia_blockchain\chia
mklink /j venv\Scripts\snake snake
mklink /j venv\Scripts\media media

call activate.bat

python install_helper.py || goto :error
goto :all_good

: error
pause
exit

: all_good

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python setup.py install

:: post-installation message

echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo.
echo SERPENT install complete.
echo Join the Discord server for support: https://discord.gg/yPdCmHSgMe
echo.
echo Run 'activate' to activate WILLOW's Python virtual environment and
echo 'deactivate' to, well, deactivate it.
echo.
echo Run 'gui_serpent' to run the GUI
echo.
echo Run 'serpent -h' to run the CLI interface
echo.
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

rmdir /s /q %root%\build
rmdir /s /q %root%\dist
rmdir /s /q %root%\SERPENT.egg-info

pause

deactivate