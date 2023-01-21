root=$(pwd)

# exit script when an error is detected
set -o errexit

# installation
git submodule update --progress --init --recursive --force
ln -s chia_blockchain/chia .

python3 -m venv venv
ln -s venv/bin/activate .
ln -s $(pwd)/chia_blockchain/chia venv/bin/
ln -s $(pwd)/src venv/bin/
ln -s $(pwd)/media venv/bin/

. ./activate

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 setup.py install

# post-installation message
echo "
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
SERPENT install.sh complete.
Join the Discord server for support: https://discord.gg/yPdCmHSgMe

Run '. activate' to activate SERPENT's Python virtual environment and
'deactivate' to, well, deactivate it.

Run 'serpent -h' for further instructions.
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"

rm -r $root/build
rm -r $root/dist
rm -r $root/SERPENT.egg-info