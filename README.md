# What is PiKiln? #

PiKiln is an open source web based kiln controller built to run on a Raspberry Pi.

This project is not complete just yet, but feedback and contributors are welcome.

# Quick Setup #

Download this Pre-Configured ISO for Raspbian with PiKiln and all the dependancies installed.

(There would be a link here if this project were finished)

Write the ISO to your MicroSD card and insert it into your Raspberry Pi

I prefer to use Win32DiskImager on Windows to write the image:

https://sourceforge.net/projects/win32diskimager/

Plug your Raspberry Pi in and connect to your Wifi network.

Open terminal and run this command:
`hostname -I`

Enter that IP address in your web browser on your phone or computer to access your PiKiln

# Manual Installation #

## Requirements ##

* Software
	* python 2.7
	* pip
	* Flask
	* git
* Hardware
	* Raspberry Pi 3B or later
	* Class 10 MicroSD card 16GB or more
	* Adafruit MCP9600 Module
	* K Type Thermocouple
	* Two 40 Amp Solid State Relays
	* 100A 50ma Non Invasive Current Sensor
	* ADC ADS1115 Module
	* Electric Kiln

## Software Setup ##

Install NOOBS or latest Raspbian ISO and write to MicroSD card

https://www.raspberrypi.org/downloads/

I prefer to use Win32DiskImager on Windows to write the image:

https://sourceforge.net/projects/win32diskimager/

After the image is written to the MicroSD card eject it and insert it into the Raspberry Pi. Plug in the Raspberry Pi and wait for the installation to complete.

## Update to latest version: ##

Connect your Raspberry Pi to your Wifi network

Open Terminal and run these commands to update your Raspberry Pi:

`sudo apt-get update

sudo apt-get upgrade -y`

Reboot your Raspberry Pi

`sudo reboot`

## Configure Raspberry Pi ##

We need to change some settings on the Raspberry Pi

Go to:

* Home > Settings > Raspberry Pi Configuration

Get rid of black overscan edges
* System > Overscan = Disable

### Enable SSH & VNC for remote access ###
* Interfaces > SSH = Enable
* Interfaces > VNC = Enable

### Enable SPI, I2C, Serial Port, Serial Console, 1-Wire, and GPIO for sensors ###
* Interfaces > SPI = Enable
* Interfaces > I2C = Enable
* Interfaces > Serial Port = Enable
* Interfaces > Serial Console = Enable
* Interfaces > 1-Wire = Enable
* Interfaces > GPIO = Enable

## Install Dependencies ##

Install PIP, Flask, and Git

`sudo apt-get install python-pip -y

sudo pip install flask -y

sudo apt-get install git -y`

Download latest release of PiKiln

`git clone https://github.com/CurlyTaleGamesLLC/PiKiln.git ~/PiKiln`

### Start Up And Settings ###

Add Flask Server to Startup

`sudo nano /etc/rc.local`

Scroll down, and just before the exit 0 line, enter the following:

`python /home/pi/PiKiln/app.py &`

You need the & at the end.

Disable screen sleeping - Optional, but handy

`sudo nano /etc/lightdm/lightdm.conf`

Look for the line starts “xserver-command” under “[Seat:*]” section and modify as below:

`xserver-command=X -s 0 -dpms`

# Features to be developed in the future #
* Delayed Start
* Temperature Email Notification - triggered via firing schedule
* GPIO output for venting with a fan - triggered via firing schedule