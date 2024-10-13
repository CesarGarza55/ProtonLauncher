import sys
import os
import json
import time
import webbrowser
from PyQt5 import QtWidgets, QtCore, QtGui
from tkinter import messagebox
from launcher import create_game_script, create_shortcut

# Create the ~/.protonlauncher directory if it doesn't exist
if not os.path.exists(os.path.expanduser("~/.protonlauncher")):
    os.makedirs(os.path.expanduser("~/.protonlauncher"))
    # Download the default icon to the ~/.protonlauncher directory
    icon_url = ""
    icon_path = os.path.expanduser("~/.protonlauncher/icon.png")
    os.system(f"wget {icon_url} -O {icon_path}")


app_dir = os.path.expanduser("~/.protonlauncher")
icon_path = os.path.join(app_dir, "icon.png")

class EditGameDialog(QtWidgets.QDialog):
    def __init__(self, game_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Game")
        self.setGeometry(100, 100, 500, 250)
        self.game_data = game_data

        layout = QtWidgets.QFormLayout(self)

        self.name_edit = QtWidgets.QLineEdit(self.game_data["name"])
        self.path_edit = QtWidgets.QLineEdit(self.game_data["path"])
        self.icon_edit = QtWidgets.QLineEdit(self.game_data["icon"])
        self.proton_edit = QtWidgets.QComboBox()
        self.proton_edit.addItems(parent.get_installed_proton_versions())
        self.proton_edit.setCurrentText(self.game_data["proton"])

        layout.addRow("Name:", self.name_edit)

        # Layout para el campo de ruta y el botón de navegación
        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        self.browse_path_button = QtWidgets.QPushButton("Browse")
        self.browse_path_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.browse_path_button)
        layout.addRow("Path:", path_layout)

        # Layout para el campo de icono y el botón de navegación
        icon_layout = QtWidgets.QHBoxLayout()
        icon_layout.addWidget(self.icon_edit)
        self.browse_icon_button = QtWidgets.QPushButton("Browse")
        self.browse_icon_button.clicked.connect(self.browse_icon)
        icon_layout.addWidget(self.browse_icon_button)
        layout.addRow("Icon:", icon_layout)

        layout.addRow("Proton Version:", self.proton_edit)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

    def browse_path(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Game", "", "Executables (*.exe)")
        if path:
            self.path_edit.setText(path)

    def browse_icon(self):
        icon, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.jpg *.jpeg)")
        if icon:
            self.icon_edit.setText(icon)

    def get_game_data(self):
        return {
            "name": self.name_edit.text(),
            "path": self.path_edit.text(),
            "icon": self.icon_edit.text(),
            "proton": self.proton_edit.currentText()
        }
    
class ProtonLauncher(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_games()

    def initUI(self):
        self.setWindowTitle("ProtonLauncher")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QtGui.QIcon(icon_path))
        # Menú de barra de herramientas
        self.toolbar = QtWidgets.QToolBar()
        self.add_game_action = QtWidgets.QAction(QtGui.QIcon("icons/add.png"), "Add Game", self)
        self.add_game_action.triggered.connect(self.add_game)
        self.toolbar.addAction(self.add_game_action)

        self.modify_game_action = QtWidgets.QAction(QtGui.QIcon("icons/edit.png"), "Modify Game", self)
        self.modify_game_action.triggered.connect(self.modify_game)
        self.toolbar.addAction(self.modify_game_action)

        self.delete_game_action = QtWidgets.QAction(QtGui.QIcon("icons/delete.png"), "Delete Game", self)
        self.delete_game_action.triggered.connect(self.delete_game)
        self.toolbar.addAction(self.delete_game_action)

        self.launch_game_action = QtWidgets.QAction(QtGui.QIcon("icons/play.png"), "Launch Game", self)
        self.launch_game_action.triggered.connect(self.launch_game)
        self.toolbar.addAction(self.launch_game_action)

        self.create_shortcut_action = QtWidgets.QAction(QtGui.QIcon("icons/shortcut.png"), "Create Shortcut", self)
        self.create_shortcut_action.triggered.connect(self.create_shortcut)
        self.toolbar.addAction(self.create_shortcut_action)

        # Selector de versión de Proton
        self.proton_label = QtWidgets.QLabel("Select Proton Version:")
        self.proton_dropdown = QtWidgets.QComboBox()
        self.proton_dropdown.addItems(self.get_installed_proton_versions())

        # Lista de juegos
        self.game_list = QtWidgets.QListWidget()
        self.game_list.itemSelectionChanged.connect(self.update_game_details)
        self.game_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.game_list.customContextMenuRequested.connect(self.show_context_menu)
        self.game_list.setIconSize(QtCore.QSize(50, 50))
        self.game_list.setStyleSheet("QListWidget::item { height: 50px; }")

        # Área de detalles del juego
        self.game_details = QtWidgets.QTextEdit()
        self.game_details.setReadOnly(True)

        # Layout principal
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.proton_label)
        main_layout.addWidget(self.proton_dropdown)

        # Layout de juegos y detalles con QSplitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.game_list)
        splitter.addWidget(self.game_details)
        splitter.setStretchFactor(0, 1)  # Proporción de estiramiento para la lista de juegos
        splitter.setStretchFactor(1, 1)  # Proporción de estiramiento para el área de detalles

        main_layout.addWidget(splitter)
        main_layout.setStretchFactor(splitter, 1)  # Proporción de estiramiento para el splitter

        self.setLayout(main_layout)

        # Crear un atajo de teclado para la tecla Delete
        delete_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self)
        delete_shortcut.activated.connect(self.delete_game)

    def get_installed_proton_versions(self):
        # Busca versiones de Proton-GE instaladas
        if not os.path.exists(os.path.expanduser("~/.steam/root/compatibilitytools.d")):
            return []
        proton_dir = os.path.expanduser("~/.steam/root/compatibilitytools.d")
        return [d for d in os.listdir(proton_dir) if os.path.isdir(os.path.join(proton_dir, d))]

    def add_game(self):
        game_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccionar Juego", "", "Ejecutables (*.exe)")
        if game_path:
            game_name = os.path.basename(game_path).replace('.exe', '')
            
            # Verificar si el juego ya existe en la lista
            if any(game["name"] == game_name for game in self.games):
                QtWidgets.QMessageBox.warning(self, "Warning", "This game is already in the list")
                return
            
            messagebox.showinfo("Icon", "Select an icon for the game, it's recommended to use an image with a 1:1 aspect ratio, if you don't select an icon, the default icon will be used.")
            icon, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.jpg *.jpeg)")
            if not icon:  # Si no se selecciona un icono, usar el icono predeterminado
                global icon_path
                icon = os.path.expanduser(icon_path)
            
            # Mostrar cuadro de diálogo para editar el nombre del juego
            new_game_name, ok = QtWidgets.QInputDialog.getText(self, "Edit Game Name", "Enter the name for the game:", QtWidgets.QLineEdit.Normal, game_name)
            if ok and new_game_name:
                game_name = new_game_name
            
            # Reemplazar espacios en el nombre del juego
            safe_game_name = game_name.replace(' ', '')
            
            prefix = f".proton-{safe_game_name}-prefix"
            game_dir = os.path.join(app_dir, safe_game_name)
            script_path = os.path.join(game_dir, f"{safe_game_name}.sh")
            
            game_data = {
                "name": game_name,
                "path": game_path,
                "prefix": prefix,
                "proton": self.proton_dropdown.currentText(),
                "icon": icon
            }

            # Crea el script del juego
            create_game_script(game_data)

            # Almacena la información del juego
            self.games.append(game_data)
            self.save_games()
            self.update_game_list()

    def modify_game(self):
        selected_game = self.game_list.currentItem()
        if selected_game:
            game_name = selected_game.text()
            game_data = next((g for g in self.games if g["name"] == game_name), None)
            if game_data:
                dialog = EditGameDialog(game_data, self)
                if dialog.exec_() == QtWidgets.QDialog.Accepted:
                    updated_game_data = dialog.get_game_data()
                    old_game_name = game_data["name"]
                    game_data.update(updated_game_data)

                    # Verificar si el nombre del juego ha cambiado
                    if old_game_name != updated_game_data["name"]:
                        # Eliminar el directorio antiguo
                        old_game_dir = os.path.join(app_dir, old_game_name.replace(' ', ''))
                        os.system(f"rm -rf {old_game_dir}")

                    # Actualizar el script del juego
                    create_game_script(game_data)

                    # Guardar los cambios
                    self.save_games()
                    self.update_game_list()
                    self.update_game_details()

    def delete_game(self, confirm="yes"):
        selected_game = self.game_list.currentItem()
        if selected_game:
            game_name = selected_game.text()
            if confirm != "no":
                if not QtWidgets.QMessageBox.question(self, "Delete Game", "Are you sure you want to delete this game from the launcher? This will not delete the game from your system.", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
                    return

            # Eliminar el juego de la lista
            self.games = [g for g in self.games if g["name"] != game_name]
            self.save_games()
            self.update_game_list()
            self.game_details.clear()

            # Eliminar la carpeta del juego
            game_dir = os.path.join(app_dir, game_name.replace(' ', ''))
            os.system(f"rm -rf {game_dir}")

    def save_games(self):
        with open(os.path.join(app_dir, "games.json"), "w") as f:
            json.dump(self.games, f)

    def load_games(self):
        if os.path.exists(os.path.join(app_dir, "games.json")):
            with open(os.path.join(app_dir, "games.json"), "r") as f:
                self.games = json.load(f)
        else:
            self.games = []
        self.update_game_list()

    def update_game_list(self):
        self.game_list.clear()
        for game in self.games:
            item = QtWidgets.QListWidgetItem(game["name"])
            icon = QtGui.QIcon(game.get("icon", os.path.expanduser(icon_path)))
            pixmap = icon.pixmap(128, 128)  # Ajusta el tamaño según sea necesario
            item.setIcon(QtGui.QIcon(pixmap))
            self.game_list.addItem(item)

    def update_game_details(self):
        selected_game = self.game_list.currentItem()
        if selected_game:
            game_name = selected_game.text()
            game_data = next((g for g in self.games if g["name"] == game_name), None)
            if game_data:
                details = f"Nombre: {game_data['name']}\n"
                details += f"Ruta: {game_data['path']}\n"
                details += f"Prefijo: {game_data['prefix']}\n"
                details += f"Proton: {game_data['proton']}\n"
                details += f"Icono: {game_data['icon']}\n"
                self.game_details.setText(details)

    def launch_game(self):
        selected_game = self.game_list.currentItem()
        if selected_game:
            game_name = selected_game.text()
            game_data = next((g for g in self.games if g["name"] == game_name), None)
            if game_data:
                game_dir = os.path.join(app_dir, game_data["name"].replace(' ', ''))
                script_path = os.path.join(game_dir, game_data["name"].replace(' ', '') + ".sh")
                os.system(f"bash {script_path}")

    def create_shortcut(self):
        selected_game = self.game_list.currentItem()
        if selected_game:
            game_name = selected_game.text()
            game_data = next((g for g in self.games if g["name"] == game_name), None)
            if game_data:
                create_shortcut(game_data)

    def show_context_menu(self, position):
        menu = QtWidgets.QMenu()
        launch_action = menu.addAction(QtGui.QIcon("icons/play.png"), "Launch Game")
        modify_action = menu.addAction(QtGui.QIcon("icons/edit.png"), "Modify Game")
        delete_action = menu.addAction(QtGui.QIcon("icons/delete.png"), "Delete Game")
        shortcut_action = menu.addAction(QtGui.QIcon("icons/shortcut.png"), "Create Shortcut")

        launch_action.triggered.connect(self.launch_game)
        modify_action.triggered.connect(self.modify_game)
        delete_action.triggered.connect(self.delete_game)
        shortcut_action.triggered.connect(self.create_shortcut)

        menu.exec_(self.game_list.viewport().mapToGlobal(position))

    def showWarnings(self):
        if not os.path.exists(os.path.expanduser("~/.steam/root/compatibilitytools.d")):
            QtWidgets.QMessageBox.warning(self, "Proton Not Found", "Proton not found in ~/.steam/root/compatibilitytools.d, please install Proton-GE or another version of Proton.")

        if not os.path.exists(os.path.expanduser(icon_path)):
            QtWidgets.QMessageBox.warning(self, "Icon Not Found", "Icon not found in ~/.protonlauncher, please add an icon.png file to this directory.")

        if not self.games:
            QtWidgets.QMessageBox.information(self, "Welcome to ProtonLauncher", "You don't have any games added to the launcher, click on 'Add Game' to add a game.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    launcher = ProtonLauncher()
    launcher.show()
    launcher.showWarnings()
    sys.exit(app.exec_())