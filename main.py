import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidget, QTextEdit, QSplitter, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont


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


        # Zoom In and Zoom Out shortcuts
        zoom_in_action = self.menu.addAction("Zoom In", self.zoom_in)
        zoom_in_action.setShortcut("Ctrl+=")

        zoom_out_action = self.menu.addAction("Zoom Out", self.zoom_out)
        zoom_out_action.setShortcut("Ctrl+-")

        reset_zoom_action = self.menu.addAction("Reset Zoom", self.reset_zoom)
        reset_zoom_action.setShortcut("Ctrl+0")



        self.current_folder = None

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.current_folder = folder
            self.file_tree.clear()
            # Use invisibleRootItem to add top-level items
            root_item = self.file_tree.invisibleRootItem()
            self.add_items_to_tree(root_item, folder)


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


    def load_file(self, item):
        # Get the file path by traversing the tree structure
        path = [item.text(0)]
        parent = item.parent()
        while parent is not None:
            path.insert(0, parent.text(0))
            parent = parent.parent()
        file_path = os.path.join(self.current_folder, *path)

        # Load the file content into the text editor
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                self.text_editor.setPlainText(content)
                self.current_file = file_path

    def save_file(self):
        if hasattr(self, 'current_file'):
            with open(self.current_file, 'w') as f:
                f.write(self.text_editor.toPlainText())
                self.statusBar().showMessage("File Saved!", 2000)


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