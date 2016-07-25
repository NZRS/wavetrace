
## Installation Requirements ##

Wavetrace has been tested with Ubuntu 12.04 and 14.04.  It should work adequately with other Linux based systems though it has caused issues on OSX.

    sudo apt-get update
    sudo apt-get install gdal-bin python-setuptools splat unzip git
    sudo easy_install pip
    sudo pip install requests BeautifulSoup
    git clone https://github.com/NZRegistryServices/wavetrace.git

## Virtual Envorinment Setup ##

If you would prefer to setup in a VirtualEnv (recommended for isolation);

    mkvirtualenv wavetrace   # creates and starts the virtual env
    # See http://docs.python-guide.org/en/latest/dev/virtualenvs/
    (wavetrace) pip install BeautifulSoup
    (wavetrace) pip install requests # required for get_data.py

