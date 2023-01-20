@echo off

:: installation

git submodule update --init
mklink /j chia chia_blockchain\chia

python -m venv .
:: Windows doesn't allow the creation of symlinks without special priviledges, so hardlinks are created instead.
mklink /h activate.bat Scripts\activate.bat
call activate.bat

pip install -r requirements.txt
python setup.py install

deactivate

:: post-installation message

echo.
echo SERPENT install.sh complete.
echo Join the Discord server for support: https://discord.gg/yPdCmHSgMe
echo.
echo Run 'activate' to activate SERPENT's Python virtual environment and 
echo 'deactivate' to, well, deactivate it.
echo.
echo Run 'gui_serpent' to run the GUI.
echo.
echo Run 'serpent -h' for further instructions.
echo.