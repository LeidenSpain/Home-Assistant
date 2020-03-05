# https://community.home-assistant.io/t/hass-update-with-bash-script/69880/5
# usermod -a -G sudo homeassistant
# https://www.home-assistant.io/docs/installation/raspberry-pi/

#! /bin/bash
# sudo -u homeassistant -H -s
source /srv/homeassistant/bin/activate
pip3 install --upgrade homeassistant




# https://community.home-assistant.io/t/hass-update-with-bash-script/69880/5
# usermod -a -G sudo homeassistant
# https://www.home-assistant.io/docs/installation/raspberry-pi/
# https://community.home-assistant.io/t/script-that-stops-hass-updates-hass-and-starts-hass-again/3330/11

 
#!/bin/bash
sudo systemctl stop home-assistant@homeassistant

# Open a shell as the homeassistant user running the Homeassistant service
# and that has ownership over the Home Assistant installation.
sudo -u homeassistant -H -s <<'EOF'

# Change into the virtual Python environment at /srv/homeassistant/
# containing the Home Assistant installation.
source /srv/homeassistant/bin/activate

# Upgrade the Home Assistant installation to the latest release.
pip3 install --upgrade homeassistant

# Exit the shell and return to the pi user.
exit
EOF

# Restart the Home Assistant service.
sudo systemctl restart home-assistant@homeassistant




#!/bin/bash
#sudo -u homeassistant -H -s

# read -rsp $'Press enter to continue...\n'
#source /srv/homeassistant/bin/activate

# read -rsp $'Press enter to continue...\n'
#pip3 install --upgrade homeassistant



https://domology.es/scripts-y-comandos-ssh-en-home-assistant/





sudo systemctl stop home-assistant@homeassistant && source /srv/homeassistant/bin/activate && pip3 install --upgrade homeassistant && exit && sudo systemctl restart home-assistant@homeassistant
