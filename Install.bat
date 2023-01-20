@echo off

set root=%cd%

:: installation

git submodule update --progress --init --recursive --force
mklink /j chia chia_blockchain\chia

python -m venv venv
:: Windows doesn't allow the creation of symlinks without special priviledges, so hardlinks are created instead.
mklink /h activate.bat venv\Scripts\activate.bat
call activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python setup.py install

mklink /j venv\Scripts\chia chia_blockchain\chia
mklink /j venv\Scripts\src src
mklink /j venv\Scripts\media media

:: post-installation message

echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo.
echo SERPENT install complete.
echo Join the Discord server for support: https://discord.gg/yPdCmHSgMe
echo.
echo Run 'activate' to activate SERPENT's Python virtual environment and 
echo 'deactivate' to, well, deactivate it.
echo.
echo Run 'GUI_SERPENT' to run the GUI.
echo.
echo Run 'SERPENT -h' for further instructions.
echo.
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

rmdir /s /q %root%\build
rmdir /s /q %root%\dist
rmdir /s /q %root%\SERPENT.egg-info

deactivate