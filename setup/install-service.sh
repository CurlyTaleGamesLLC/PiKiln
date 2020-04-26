#!/bin/bash
sudo cp /home/pi/PiKiln/libraries/pikiln.service /etc/systemd/system/
sudo systemctl enable pikiln
