#!/bin/bash
APP_DIR="/home/nidec-sever-agv/printer_deploy/iwms_printer_qml"
cd "$APP_DIR" || exit 1
"$APP_DIR/venv/bin/python" -m src.main
echo
read -p "Press Enter to close..."
