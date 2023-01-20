# exit script when an error is detected
set -o errexit

# help message

HELP="\
Usage: $0 [-sh]

    -s    Upgrade setuptools in SERPENT's Python virtual environment. Use this
          if the installation isn't working without it.
    -h    Display this help message and exits.
"

help()
{
    echo "$HELP"
}

# argument handling

while getopts sh flag
do
    case "${flag}" in
        s) SETUPTOOLS=setuptools;;
        h) help; exit 0;;
        *) help; exit 1;;
    esac
done

# installation

PACKAGES='python3.7-minimal python3-venv python3.7-venv'

# check if $PACKAGES are already installed
dpkg -s $PACKAGES

# if they aren't already installed...
if [ $? -ne 0 ]
then
    sudo apt update
    sudo apt install $PACKAGES
fi

git submodule update --init
ln -s chia_blockchain/chia .

python3.7 -m venv .
ln -s bin/activate .
. ./activate

pip3 install -U pip $SETUPTOOLS
pip3 install -r requirements.txt

python setup.py develop

# post-installation message

echo "
SERPENT install.sh complete.
Join the Discord server for support: https://discord.gg/yPdCmHSgMe

Run '. ./bin/activate' to activate SERPENT's Python virtual environment and
'deactivate' to, well, deactivate it.

Run 'serpent -h' for further instructions.
"