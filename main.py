import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidget, QTextEdit, QSplitter, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont

import json



# Config files for saving the last opened file
def load_config():
    """Load configuration from config.json, or return default structure."""
    default_config = {
        "last_opened_folder": None,
        "favorite_folders": {}
    }
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is corrupted, return the default config
        return default_config

def save_config(config):
    """Save configuration to config.json."""
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)  # Use indent for readability


#Main class for Note App Layout and Functionality
class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Super Ultra Mega Note APP")
        self.resize(800, 600)




        """ Sidebar to list files
        #self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_file)
        self.file_list.setMinimumWidth(100)
        self.file_list.setMaximumWidth(800)
        self.file_list.setSizePolicy(QListWidget().sizePolicy())
         """
        # Sidebar Tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.itemClicked.connect(self.load_file)

            # Load configuration
        self.config = load_config()
        self.current_folder = self.config.get("last_opened_folder")

        # Automatically load last opened folder
        if self.current_folder:
            self.load_folder(self.current_folder)
        else:
            self.statusBar().showMessage("No folder was previously loaded.", 2000)




        # Text editor for viewing/editing
        self.text_editor = ZoomableTextEdit(self)

        # Splitter for making resizable layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.file_tree)
        splitter.addWidget(self.text_editor)
        splitter.setSizes([400, 400])

        #Main layout
        layout = QVBoxLayout()
        layout.addWidget(splitter)


        #Set the layout to a container widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Add menu for importing folder
        self.menu = self.menuBar().addMenu("File")

        open_action = self.menu.addAction("Open Folder", self.open_folder)
        open_action.setShortcut("Ctrl+O")
        
        save_action = self.menu.addAction("Save", self.save_file)
        save_action.setShortcut("Ctrl+S")

        # Add "Home" menu
        home_menu = self.menuBar().addMenu("Home")

        # Add actions to view and manage favorites
        view_favorites_action = home_menu.addAction("View Favorites", self.show_favorites)
        add_favorite_action = home_menu.addAction("Add to Favorites", self.prompt_add_favorite)


        # Zoom In and Zoom Out shortcuts
        zoom_in_action = self.menu.addAction("Zoom In", self.zoom_in)
        zoom_in_action.setShortcut("Ctrl+=")

        zoom_out_action = self.menu.addAction("Zoom Out", self.zoom_out)
        zoom_out_action.setShortcut("Ctrl+-")

        reset_zoom_action = self.menu.addAction("Reset Zoom", self.reset_zoom)
        reset_zoom_action.setShortcut("Ctrl+0")

        fullscreen_action = self.menu.addAction("Toggle Fullscreen", self.toggle_fullscreen)
        fullscreen_action.setShortcut("F11")

        windowed_fullscreen_action = self.menu.addAction("Toggle Windowed Fullscreen", self.toggle_windowed_fullscreen)
        windowed_fullscreen_action.setShortcut("Ctrl+F11")

           # Automatically load last opened folder
        if self.current_folder:
            self.load_folder(self.current_folder)

       

    def add_favorite(self, label, folder_path):
                """Add a folder shortcut to the favorites."""
                if "favorite_folders" not in self.config:
                    self.config["favorite_folders"] = {}  # Ensure the key exists

                self.config["favorite_folders"][label] = folder_path
                save_config(self.config)
                self.statusBar().showMessage(f"Added '{label}' to favorites.", 2000)

    def remove_favorite(self, label):
            """Remove a folder shortcut from the favorites."""
            if "favorite_folders" in self.config and label in self.config["favorite_folders"]:
                del self.config["favorite_folders"][label]
                save_config(self.config)
                self.statusBar().showMessage(f"Removed '{label}' from favorites.", 2000)

    def load_favorite(self, label):
            """Load a folder from the favorites."""
            if "favorite_folders" in self.config and label in self.config["favorite_folders"]:
                folder_path = self.config["favorite_folders"][label]
                self.load_folder(folder_path)
            else:
                self.statusBar().showMessage(f"Favorite '{label}' not found.", 2000)

    def show_favorites(self):
            """Display a list of favorites for quick access."""
            if "favorite_folders" not in self.config or not self.config["favorite_folders"]:
                self.statusBar().showMessage("No favorites available.", 2000)
                return

            from PyQt5.QtWidgets import QInputDialog
            labels = list(self.config["favorite_folders"].keys())
            label, ok = QInputDialog.getItem(self, "Select Favorite", "Choose a folder to open:", labels, editable=False)
            if ok and label:
                self.load_favorite(label)
    def prompt_add_favorite(self):
            """Prompt the user to add a folder to favorites."""
            folder = QFileDialog.getExistingDirectory(self, "Select Folder to Add to Favorites")
            if not folder:
                return

            from PyQt5.QtWidgets import QInputDialog
            label, ok = QInputDialog.getText(self, "Add Favorite", "Enter a label for this folder:")
            if ok and label:
                self.add_favorite(label, folder)


    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.current_folder = folder
            self.file_tree.clear()
            # Use invisibleRootItem to add top-level items
            root_item = self.file_tree.invisibleRootItem()
            self.add_items_to_tree(root_item, folder)
            self.config["last_opened_folder"] = folder
            save_config(self.config)


    def add_items_to_tree(self, parent_item, folder):
        for item in os.listdir(folder):

            if item == ".git":
                continue
            item_path = os.path.join(folder, item)
            if os.path.isdir(item_path):  # If it's a folder
                folder_item = QTreeWidgetItem([item])
                folder_item.setIcon(0, self.style().standardIcon(4))  # Folder icon
                parent_item.addChild(folder_item)  # Add folder as a child
                self.add_items_to_tree(folder_item, item_path)  # Recursively add subfolders and files
            elif item.endswith(('.txt', '.md')):  # If it's a file
                file_item = QTreeWidgetItem([item])
                file_item.setIcon(0, self.style().standardIcon(2))  # File icon
                parent_item.addChild(file_item)  # Add file as a child
    def load_folder(self, folder):
        """Reusable method to load a folder into the sidebar."""
        if not folder:
            self.statusBar().showMessage("No folder specified.", 2000)
            return

        self.current_folder = folder
        self.file_tree.clear()
        root_item = self.file_tree.invisibleRootItem()
        self.add_items_to_tree(root_item, folder)

    def load_file(self, item):
        # Ensure that a folder is loaded
        if not self.current_folder:
            self.statusBar().showMessage("No folder loaded. Please open a folder first.", 2000)
            return

        # Get the file path by traversing the tree structure
        path = [item.text(0)]
        parent = item.parent()
        while parent is not None:
            path.insert(0, parent.text(0))
            parent = parent.parent()
        
        # Join the folder path with the item path
        file_path = os.path.join(self.current_folder, *path)

        # Load the file content into the text editor
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    self.text_editor.setPlainText(content)
                    self.current_file = file_path
            except Exception as e:
                self.statusBar().showMessage(f"Error opening file: {str(e)}", 2000)
        else:
            self.statusBar().showMessage("Selected item is not a valid file.", 2000)

    def save_file(self):
        if hasattr(self, 'current_file'):
            with open(self.current_file, 'w') as f:
                f.write(self.text_editor.toPlainText())
                self.statusBar().showMessage("File Saved!", 2000)

    #Functions for zooming
    def scale_tree(self, zoom_level):
        """Adjusts the font size of the tree view based on the zoom level."""
        new_font_size = max(8, 12 + zoom_level)  # Ensure font size is at least 8
        font = self.file_tree.font()
        font.setPointSize(new_font_size)
        self.file_tree.setFont(font)
    def zoom_in(self):
        self.text_editor.zoom_in()
        self.scale_tree(self.text_editor.zoom_level)

    def zoom_out(self):
        self.text_editor.zoom_out()
        self.scale_tree(self.text_editor.zoom_level)

    def reset_zoom(self):
        self.text_editor.reset_zoom()
        self.scale_tree(self.text_editor.zoom_level)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def toggle_windowed_fullscreen (self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    





class ZoomableTextEdit(QTextEdit):
    def __init__(self, note_app, parent=None):
        super().__init__(parent)
        self.note_app = note_app
        self.zoom_level = 0  # Track zoom level for resetting
        self.default_font_size = 12  # Default font size

        # Set initial font
        self.font = QFont()
        self.font.setPointSize(self.default_font_size)
        self.setFont(self.font)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:  # Scroll up
                self.zoom_in()
            else:  # Scroll down
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def zoom_in(self):
        self.zoom_level += 1
        self.update_font_size()
        self.note_app.scale_tree(self.zoom_level)  # Notify parent

    def zoom_out(self):
        if self.zoom_level > -self.default_font_size + 1:  # Prevent font size from going negative
            self.zoom_level -= 1
            self.update_font_size()
            self.note_app.scale_tree(self.zoom_level)  # Notify parent

    def reset_zoom(self):
        self.zoom_level = 0 
        self.update_font_size()
        self.note_app.scale_tree(self.zoom_level)  # Notify parent

    def update_font_size(self):
        # Calculate new font size
        new_font_size = self.default_font_size + self.zoom_level
        if new_font_size > 1:  # Ensure font size remains positive
            self.font.setPointSize(new_font_size)
            self.setFont(self.font)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()
    window.show()
    sys.exit(app.exec_())
