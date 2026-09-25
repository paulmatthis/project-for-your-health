#!/bin/bash
# Double-click this to open the dashboard. See
# app/open_dashboard.sh for what it actually does (syncs the workbook,
# starts the server for just this session, opens it in its own Chrome
# window, shuts everything down again when that window is closed).
cd "$(dirname "$0")"
./app/open_dashboard.sh
