#########
# Intro #
#########
echo "This script will install WitSpec into a virtual environment. Make
sure that you are not already sourced in another environment. The VE will
be created and installed to $HOME/witspec_ve."
echo ""

echo -n "Do you wish to proceed? (y/n): "
read proceed

if [ "$proceed" = "y" ]; then
    echo "starting install..."
    basedir=$(pwd)
else
    echo "exiting..."
    exit
fi

##################################
# Create the virtual environment #
##################################
cd $HOME

# Make sure virtualenv exists
if hash virtualenv 2> /dev/null; then
    virtualenv witspec_ve
else
    echo "Need to install virtualenv"
    echo -n "Install it now? (y/n): "
    read install

    if [ "$install" = "n" ]; then
        echo "exiting..."
        exit
    else
        echo "installing virtualenv..."
        pip install virtualenv
        virtualenv witspec_ve
    fi
fi

# source the VE
source $HOME/witspec_ve/bin/activate
pip install numpy

#####################################
# Install the repo and dependencies #
#####################################
# Install WitSpec
cd $basedir
pip install -r requirements.txt && pip install -e .

# Install nds2
cd $HOME/witspec_ve
wget http://www.lsc-group.phys.uwm.edu/daswg/download/software/source/nds2-client-0.15.2.tar.gz
tar -xzvf nds2-client-0.15.2.tar.gz
mv nds2-client-0.15.2.tar.gz nds2-client-0.15.2/
cd $HOME/witspec_ve/nds2-client-0.15.2/
mkdir obj
cd obj
cmake -DCMAKE_INSTALL_PREFIX=$HOME/witspec_ve/ -DCMAKE_C_COMPILER=$(which cc) -DCMAKE_CXX_COMPILER=$(which c++) ..
cmake --build .
cmake --build . -- install

##########
# Finish #
##########
echo "Done with install"
