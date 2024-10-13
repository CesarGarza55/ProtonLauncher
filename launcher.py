import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from config import load_desktop, set_desktop
home = os.path.expanduser("~")
app_dir = os.path.expanduser("~/.protonlauncher")

def create_game_script(game_data):
    game_dir = os.path.join(app_dir, game_data["name"].replace(' ', ''))
    os.makedirs(game_dir, exist_ok=True)
    
    script_path = os.path.join(game_dir, f"{game_data['name'].replace(' ', '')}.sh")
    with open(script_path, 'w') as f:
        f.write(f"""#!/bin/bash

# Establecer las variables necesarias para Proton
export STEAM_COMPAT_DATA_PATH="$HOME/{game_data['prefix']}"
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.steam/root"
export STEAM_COMPAT_LIBRARY_PATHS="$HOME/.steam/steamapps"

# Crear el prefijo si no existe
if [ ! -d "$STEAM_COMPAT_DATA_PATH" ]; then
    echo "Creando el prefijo de Proton..."
    mkdir -p "$STEAM_COMPAT_DATA_PATH"
    
    # Inicializar el prefijo de Proton (esto puede tardar un momento)
    $HOME/.steam/root/compatibilitytools.d/{game_data["proton"]}/proton init "$STEAM_COMPAT_DATA_PATH"
fi

# Ejecutar el juego con Proton-GE
$HOME/.steam/root/compatibilitytools.d/{game_data["proton"]}/proton run \\
"{game_data['path']}"
""")
    os.chmod(script_path, 0o755)  # Hacer el script ejecutable

def get_desktop_directory():
    # Intentar obtener el directorio del escritorio desde la variable de entorno
    desktop_dir = os.getenv("XDG_DESKTOP_DIR")
    if desktop_dir and os.path.exists(desktop_dir):
        set_desktop(desktop_dir)
        return desktop_dir

    # Comprobar nombres comunes del directorio del escritorio
    common_desktop_dirs = ["Desktop", "Escritorio"]
    for d in common_desktop_dirs:
        desktop_path = os.path.join(home, d)
        if os.path.exists(desktop_path):
            set_desktop(desktop_path)
            return desktop_path
    
    # Retorna None si no se encuentra ninguno
    return None

def create_shortcut(game_data):
    # Intenta obtener el directorio del escritorio del archivo de configuraciones
    desktop_dir = load_desktop()
    if not desktop_dir:
        desktop_dir = get_desktop_directory()
    if not desktop_dir:
        # ask for the desktop directory
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("The desktop directory could not be found automatically, please select it manually.")
        msg.setWindowTitle("Desktop Directory Not Found")
        msg.exec_()
        desktop_dir = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Desktop Directory")
        
        if desktop_dir:
            set_desktop(desktop_dir)
        if not desktop_dir:
            return

    desktop_file_path = os.path.join(desktop_dir, f"{game_data['name']}.desktop")
    
    with open(desktop_file_path, 'w') as f:
        f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={game_data['name']}
Exec=bash "{os.path.join(app_dir, game_data['name'].replace(' ', ''), game_data['name'].replace(' ', '') + '.sh')}"
Icon={game_data['icon']}
Terminal=false
""")
    
    # Hacer el acceso directo ejecutable
    os.chmod(desktop_file_path, 0o755)

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("The shortcut has been created successfully.")
    msg.setWindowTitle("Shortcut Created")
    msg.exec_()