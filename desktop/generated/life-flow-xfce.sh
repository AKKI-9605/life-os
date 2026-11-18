#!/usr/bin/env bash
set -euo pipefail

# Generated LIFE Flow XFCE configuration.
# Preview only until tested against the target XFCE version.
# Applying this changes existing panel configuration.

xfconf-query -c xfce4-panel -p /panels --create -t int -s 1 -t int -s 2
xfconf-query -c xfce4-panel -p /panels/panel-1/position --create -t string -s 'p=6;x=0;y=0'
xfconf-query -c xfce4-panel -p /panels/panel-1/size --create -t int -s 30
xfconf-query -c xfce4-panel -p /panels/panel-2/position --create -t string -s 'p=10;x=0;y=0'
xfconf-query -c xfce4-panel -p /panels/panel-2/size --create -t int -s 48
xfconf-query -c xfce4-panel -p /panels/panel-2/length --create -t int -s 45
