# ProHiC - Prokaryotic HiC Browser
A small cross-platform browser for prokaryotic HiC maps.

ProHiC provides handy GUI for visualizing and browsing HiC contact maps and tracks of small circular genomes.
It provides unique features, such as genome rolling, instant observed/expected map computing,
extremely convenient colorscale adjusting.

ProHiC is tested on Windows, Linux, MacOS. Portable version for Windows is also
availabe.

## Installation

### Standard installation
To install ProHiC, you should have python 3.8, 3.9 or 3.10 and pip installed on your computer. If you don't have one of them, see below. When all conditions are met, browser can be installed from github with pip. 
```
pip install https://github.com/a17sol/ProHiC/archive/master.zip
```
See **Installation details** for more for details on how to install the program on your operating system, additional steps may be necessary.

After installation it is possible to create a desktop shortcut with simple command:
```
prohic shortcut
```
On some systems (e.g. Ubuntu) you should manually allow launching in the right-button menu of the shortcut.

### Installation details

#### Windows

##### If you don't have any python on your computer
1. Download installer (e.g. <a href="https://www.python.org/ftp/python/3.9.5/python-3.9.5-amd64.exe">here</a>)
2. Run inastaller. Select options: 
	- First screen: Add Python3.9 to PATH, Customize installation
	- Second screen: Only pip and py launcher
	- Third screen: default

##### If your python is lower than 3.8, or higher than 3.10
You have three options:
1. Use a <a href="https://github.com/a17sol/ProHiC_portable">portable version</a>
2. Uninstall existing version and install 3.9 as described above. Make sure that this does not cause incompatibilities with other applications.
3. Use conda environment. It is safe, but a bit more difficult.

##### If you don't have pip on your computer
1. Download installer (<a href="https://bootstrap.pypa.io/get-pip.py">here</a>)
2. Run it as administrator

##### Finally, when everything is ready
Run cmd.exe and type
```
pip install https://github.com/a17sol/ProHiC/archive/master.zip
```

We must note, that `cooler` package depends on some Windows-incompatible packages, so modified version of `cooler` (`win_cooler`) will be installed automatically. It lacks some of the functionality, but is enough for our needs.

#### MacOS

##### If your Mac has proprietary processor
On Mac with Apple processor you always need to use conda environment with pip installed inside, as these pocessors does not support some of the standerd packages.

##### If you don't have any python on your computer
1. Download installer (e.g. <a href="https://www.python.org/ftp/python/3.9.5/python-3.9.5-macos11.pkg">here</a>)
2. Run inastaller.

##### If your python is lower than 3.8, or higher than 3.10
You have two options:
1. Uninstall existing version and install 3.9 as described above. Make sure that this does not cause incompatibilities with other applications.
2. Use conda environment. It is safe, but a bit more difficult.

##### If you don't have pip on your computer
pip always came with python, but in case you need, you can use
```
sudo apt install python3-pip
```

##### Finally, when everything is ready
Run Terminal and type
```
sudo pip install https://github.com/a17sol/ProHiC/archive/master.zip
```
In most cases "sudo" is not really necessary, but is recommended.

#### Linux

##### If you don't have any python on your computer
Note that all modern versions of Ubuntu have one version of python installed. If your preinstalled version is inappropriate, see below.
If you really need to install it, use the terminal command
```
sudo apt install python3.9
```
##### If your python is lower than 3.8, or higher than 3.10
You have two options:
1. Uninstall existing version and install 3.9 as described above. Make sure that this does not cause incompatibilities with other applications.
2. Use conda environment. It is safe, but a bit more difficult.

##### If you don't have pip on your computer
Use terminal command
```
sudo apt install python3-pip
```

##### Finally, when everything is ready
Run Terminal and type
```
sudo apt-get install libxcb-xinerama0
sudo pip install https://github.com/a17sol/ProHiC/archive/master.zip
```

### Portable version
To download the portable version for Windows, click the link: <a href="https://github.com/a17sol/ProHiC_portable/archive/master.zip">Download ProHiC_portable</a>.

Relevant repository is <a href="https://github.com/a17sol/ProHiC_portable">ProHiC_portable</a>

### Uninstallation
To uninstall browser just use 
```
pip uninstall ProHiC
```
Note that desktop shortcut should be removed manually.

## Usage
You can start browser with command
```
prohic
```
or by clicking desktop shortcut.

All functioanality is available though GUI, and main functions - though key bindings.

Note the functionality, that could be not obvious enough:
* Click on gene/region shows its name and info
* Click on Y-axis of graph track toggles logarithmic mode
* Right-click on map provides "View all" option and allows to export view
* Right-click menu of graph-tracks allows to set Y-autorange to visible data only
* Right-click on colorscale resets it
* Disabling log colorscale may be useful when browsing observed/expected map

Acceptable formats:
* HiC-map - .cool, .mcool, .np (numpy savetxt files, useful option for quick testing of map processing algorithms etc.)
* Gene/region track - .bed, .gff, .gff2, .gff3
* Graph track - .bedgraph