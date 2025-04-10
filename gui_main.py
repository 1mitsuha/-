import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QLineEdit, QLabel, QMessageBox, 
    QListWidget, QListWidgetItem, QSplitter, QInputDialog, QMenu, QAction,
    QComboBox, QStyleFactory, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from note_manager import NoteManager
from models import Category, Note # Import models

class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.note_manager = NoteManager()
        self.current_category: Optional[Category] = None
        self.current_note: Optional[Note] = None
        self.init_ui()
        self.load_categories() # Load categories on startup

    def init_ui(self):
        self.setWindowTitle('笔记管理程序 v2.0')
        self.setGeometry(100, 100, 1400, 900) # Increased size
        self.setStyleSheet("""
            QMainWindow { background-color: #f8f9fa; }
            QWidget { font-size: 18px; } /* Increased base font size further */
            QListWidget { 
                border: 1px solid #ced4da; 
                border-radius: 4px; 
                background-color: white; 
                padding: 5px;
            }
            QListWidget::item { 
                padding: 8px 10px; /* Increased item padding */ 
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected { 
                background-color: #cfe2ff; 
                color: #000;
                border-left: 3px solid #0d6efd;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 10px 18px; /* Increased padding */
                border-radius: 4px;
                min-width: 90px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton#deleteButton { background-color: #dc3545; }
            QPushButton#deleteButton:hover { background-color: #bb2d3b; }
            QPushButton#secondaryButton { background-color: #6c757d; }
            QPushButton#secondaryButton:hover { background-color: #5c636a; }
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px; /* Increased padding */
                background-color: white;
            }
            QLabel { padding-top: 5px; font-weight: bold; color: #495057;}
            QSplitter::handle { background-color: #e9ecef; }
            QSplitter::handle:horizontal { width: 5px; }
            QSplitter::handle:vertical { height: 5px; }
        """)

        # --- Main Layout ---        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # Overall layout will be Vertical: Toolbar + Splitter
        overall_layout = QVBoxLayout(main_widget)

        # --- Top Toolbar ---        
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 2, 5, 2) # Reduced top/bottom margins

        global_search_label = QLabel("全局搜索:")
        self.global_search_input = QLineEdit()
        self.global_search_input.setPlaceholderText('搜索所有笔记...')
        self.global_search_input.textChanged.connect(self.perform_global_search)
        # Allow the global search input to take more space
        self.global_search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        clear_global_search_btn = QPushButton("清除搜索")
        clear_global_search_btn.setObjectName("secondaryButton")
        clear_global_search_btn.clicked.connect(self.clear_global_search)

        toolbar_layout.addWidget(global_search_label)
        toolbar_layout.addWidget(self.global_search_input)
        toolbar_layout.addWidget(clear_global_search_btn)
        toolbar_layout.addStretch() # Pushes the rest to the right

        overall_layout.addWidget(toolbar)

        # --- Splitter for Panels (Remains Horizontal) ---        
        splitter = QSplitter(Qt.Horizontal)
        overall_layout.addWidget(splitter) # Add splitter below toolbar

        # --- Panel 1: Categories ---        
        category_panel = QWidget()
        category_layout = QVBoxLayout(category_panel)
        category_layout.setContentsMargins(5, 5, 5, 5)
        
        category_label = QLabel("分类列表")
        self.category_list = QListWidget()
        self.category_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.category_list.customContextMenuRequested.connect(self.show_category_context_menu)
        self.category_list.currentItemChanged.connect(self.category_selected)

        add_category_btn = QPushButton("添加分类")
        add_category_btn.setObjectName("secondaryButton")
        add_category_btn.clicked.connect(self.add_category)

        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_list)
        category_layout.addWidget(add_category_btn)
        splitter.addWidget(category_panel)

        # --- Panel 2: Notes List (Label changes dynamically) ---        
        notes_panel = QWidget()
        notes_layout = QVBoxLayout(notes_panel)
        notes_layout.setContentsMargins(5, 5, 5, 5)
        
        self.notes_list_label = QLabel("笔记列表 (请选择分类)") # Dynamic label
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('在当前分类下搜索...')
        self.search_input.textChanged.connect(self.search_notes)
        self.note_list = QListWidget()
        self.note_list.currentItemChanged.connect(self.note_selected)
        
        self.new_note_btn = QPushButton("新建笔记")
        self.new_note_btn.clicked.connect(self.new_note)
        self.new_note_btn.setEnabled(False)

        notes_layout.addWidget(self.notes_list_label) # Add dynamic label
        notes_layout.addWidget(self.search_input)
        notes_layout.addWidget(self.note_list)
        notes_layout.addWidget(self.new_note_btn)
        splitter.addWidget(notes_panel)

        # --- Panel 3: Note Editor ---        
        editor_panel = QWidget()
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(5, 5, 5, 5)
        
        title_label = QLabel("标题:")
        self.title_input = QLineEdit()
        self.title_input.setEnabled(False)
        
        content_label = QLabel("内容:")
        self.content_input = QTextEdit()
        self.content_input.setEnabled(False)

        move_layout = QHBoxLayout()
        move_label = QLabel("移动到分类:")
        self.move_category_combo = QComboBox()
        self.move_category_combo.setEnabled(False)
        move_layout.addWidget(move_label)
        move_layout.addWidget(self.move_category_combo)
        move_layout.addStretch()
        
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_note)
        self.delete_button = QPushButton("删除")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_note)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)

        editor_layout.addWidget(title_label)
        editor_layout.addWidget(self.title_input)
        editor_layout.addWidget(content_label)
        editor_layout.addWidget(self.content_input)
        editor_layout.addLayout(move_layout)
        editor_layout.addLayout(button_layout)
        splitter.addWidget(editor_panel)

        splitter.setSizes([250, 300, 850]) # Adjust initial sizes

    # --- Global Search Methods ---
    def perform_global_search(self):
        """Performs search across all notes based on global search input."""
        keyword = self.global_search_input.text().strip()
        self.clear_note_list()
        self.clear_editor()
        self.set_editor_enabled(False)
        self.note_list.clearSelection()
        self.current_note = None

        if keyword: 
            # Optionally disable category interaction during global search
            self.category_list.setEnabled(False)
            self.notes_list_label.setText(f'全局搜索结果: "{keyword}"')
            notes = self.note_manager.search_all_notes(keyword)
            for note in notes:
                # Display category name along with title for context
                display_text = f"{note.title}  [{note.category.name}]"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, note) # Store full note object
                self.note_list.addItem(item)
            self.new_note_btn.setEnabled(False) # Can't create new note in search results
            self.search_input.setEnabled(False) # Disable category search
        else:
            # If global search is cleared, re-enable categories and load current
            self.clear_global_search() 

    def clear_global_search(self):
        """Clears global search and restores category view."""
        # Block signals to prevent triggering search again while clearing
        self.global_search_input.blockSignals(True)
        self.global_search_input.clear()
        self.global_search_input.blockSignals(False)

        self.category_list.setEnabled(True)
        self.search_input.setEnabled(True)
        # Reload notes for the currently selected category (if any)
        current_cat_item = self.category_list.currentItem()
        if current_cat_item:
            self.category_selected(current_cat_item)
            self.notes_list_label.setText(f'笔记列表 ({self.current_category.name})')
            self.new_note_btn.setEnabled(True)
        else:
            self.clear_note_list()
            self.notes_list_label.setText("笔记列表 (请选择分类)")
            self.new_note_btn.setEnabled(False)
        self.clear_editor()
        self.set_editor_enabled(False)

    # --- Category Methods ---    
    def load_categories(self):
        """Loads categories into the category list."""
        self.category_list.clear()
        self.move_category_combo.clear() # Clear move combo as well
        categories = self.note_manager.get_all_categories()
        if not categories:
             # Ensure default if none exist after init check
             default_cat = self.note_manager.add_category("Uncategorized")
             if default_cat: categories = [default_cat]
             else: return # Should not happen

        for category in categories:
            item = QListWidgetItem(category.name)
            item.setData(Qt.UserRole, category) # Store category object
            self.category_list.addItem(item)
            self.move_category_combo.addItem(category.name, category.id)
            
        # Select the first category by default if list is not empty
        if self.category_list.count() > 0:
             self.category_list.setCurrentRow(0)
             self.category_selected(self.category_list.item(0))
        else:
             self.clear_note_list()
             self.clear_editor()
             self.set_editor_enabled(False)
             self.new_note_btn.setEnabled(False)
             
        # Check global search state after loading
        if not self.global_search_input.text():
            self.category_list.setEnabled(True)
            self.search_input.setEnabled(self.category_list.count() > 0)
            if self.category_list.count() > 0:
                 self.category_list.setCurrentRow(0)
            else:
                 # Handle no categories case
                 self.notes_list_label.setText("笔记列表 (请先添加分类)")
                 self.new_note_btn.setEnabled(False)
                 self.search_input.setEnabled(False)
                 self.clear_note_list()
                 self.clear_editor()
                 self.set_editor_enabled(False)
        else:
            # If global search is active, keep categories disabled
            self.category_list.setEnabled(False)
            self.search_input.setEnabled(False)

    def category_selected(self, current_item: QListWidgetItem, previous_item: QListWidgetItem = None):
        """Handles selection of a category. Clears global search if active."""
        # If a category is selected manually, clear global search
        if self.global_search_input.text():
            self.clear_global_search()
            # Need to re-select the item because clear_global_search might change selection
            if current_item:
                 self.category_list.setCurrentItem(current_item)
            return # Let the re-selection trigger the rest
            
        if current_item:
            self.current_category = current_item.data(Qt.UserRole)
            self.notes_list_label.setText(f'笔记列表 ({self.current_category.name})') # Update label
            self.load_notes_for_category(self.current_category.id)
            self.new_note_btn.setEnabled(True)
            self.search_input.setEnabled(True) # Enable category search
            self.clear_editor()
            self.set_editor_enabled(False)
        else:
            self.current_category = None
            self.notes_list_label.setText("笔记列表 (请选择分类)") # Update label
            self.clear_note_list()
            self.new_note_btn.setEnabled(False)
            self.search_input.setEnabled(False) # Disable category search
            self.clear_editor()
            self.set_editor_enabled(False)

    def add_category(self):
        """Adds a new category via input dialog."""
        name, ok = QInputDialog.getText(self, '添加新分类', '请输入分类名称:')
        if ok and name:
            if not self.note_manager.add_category(name):
                QMessageBox.warning(self, '错误', f'分类 "{name}" 已存在或添加失败。')
            else:
                self.load_categories() # Refresh list

    def rename_category(self):
        """Renames the selected category."""
        selected_item = self.category_list.currentItem()
        if not selected_item: return
        
        category: Category = selected_item.data(Qt.UserRole)
        new_name, ok = QInputDialog.getText(self, '重命名分类', '请输入新的分类名称:', QLineEdit.Normal, category.name)
        
        if ok and new_name and new_name != category.name:
            if not self.note_manager.update_category_name(category.id, new_name):
                QMessageBox.warning(self, '错误', f'无法重命名为 "{new_name}"，可能名称已存在。')
            else:
                # Refresh lists
                current_cat_id = category.id
                self.load_categories()
                # Reselect the renamed category
                for i in range(self.category_list.count()):
                    item = self.category_list.item(i)
                    if item.data(Qt.UserRole).id == current_cat_id:
                        self.category_list.setCurrentItem(item)
                        break

    def delete_category(self):
        """Deletes the selected category and its notes."""
        selected_item = self.category_list.currentItem()
        if not selected_item: return

        category: Category = selected_item.data(Qt.UserRole)
        reply = QMessageBox.question(self, '确认删除', 
                                   f'确定要删除分类 "{category.name}" 及其所有笔记吗？此操作无法撤销。',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.note_manager.delete_category(category.id):
                self.load_categories() # Refresh category list
                # If no categories left, UI should reflect that
                if self.category_list.count() == 0:
                     self.current_category = None
                     self.clear_note_list()
                     self.new_note_btn.setEnabled(False)
                     self.clear_editor()
                     self.set_editor_enabled(False)
            else:
                QMessageBox.warning(self, '错误', '删除分类失败。')

    def show_category_context_menu(self, position):
        """Shows context menu for category list."""
        selected_item = self.category_list.itemAt(position)
        if not selected_item: return

        menu = QMenu()
        rename_action = QAction("重命名", self)
        delete_action = QAction("删除", self)
        
        rename_action.triggered.connect(self.rename_category)
        delete_action.triggered.connect(self.delete_category)
        
        menu.addAction(rename_action)
        menu.addAction(delete_action)
        
        menu.exec_(self.category_list.mapToGlobal(position))

    # --- Note Methods ---    
    def load_notes_for_category(self, category_id: int):
        """Loads notes for the selected category."""
        self.clear_note_list()
        self.current_note = None # Deselect note when category changes
        notes = self.note_manager.get_notes_by_category(category_id)
        for note in notes:
            item = QListWidgetItem(note.title)
            item.setData(Qt.UserRole, note) # Store note object
            self.note_list.addItem(item)
        self.search_notes() # Apply search filter if any

    def note_selected(self, current_item: QListWidgetItem, previous_item: QListWidgetItem = None):
        """Handles selection of a note from either category view or global search."""
        self.clear_editor()
        if current_item:
            self.current_note = current_item.data(Qt.UserRole)
            self.title_input.setText(self.current_note.title)
            self.content_input.setText(self.current_note.content)
            
            # Find the correct category in the 'move to' combo
            cat_id_to_select = self.current_note.category_id
            index = self.move_category_combo.findData(cat_id_to_select)
            if index >= 0:
                self.move_category_combo.setCurrentIndex(index)
            else: # Should not happen if data is consistent
                 self.move_category_combo.setCurrentIndex(-1)
                 
            self.set_editor_enabled(True)
            # When selecting from global search, Delete should still work, but Move might be tricky
            # Let's enable move, assuming the combo is populated correctly.
        else:
            self.current_note = None
            self.set_editor_enabled(False)

    def new_note(self):
        """Clears the editor to start a new note in the current category."""
        if not self.current_category:
             QMessageBox.warning(self, '提示', '请先选择一个分类。')
             return
        self.note_list.clearSelection() # Deselect any current note
        self.current_note = None 
        self.clear_editor()
        self.set_editor_enabled(True)
        self.title_input.setFocus()
        # Set move combo to current category for new note
        index = self.move_category_combo.findData(self.current_category.id)
        if index >= 0:
             self.move_category_combo.setCurrentIndex(index)

    def save_note(self):
        """Saves the current note (new or existing)."""
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText() # Keep leading/trailing whitespace in content
        category_id_to_save = self.move_category_combo.currentData() # Get ID from combo

        if not title:
            QMessageBox.warning(self, '警告', '笔记标题不能为空。')
            return
        if category_id_to_save is None: # Should not happen if UI logic is correct
             QMessageBox.critical(self, '错误', '无法确定要保存到的分类。')
             return

        if self.current_note: # Update existing note
            success = self.note_manager.update_note(
                self.current_note.id, title, content, category_id_to_save
            )
            if success:
                 QMessageBox.information(self, '成功', '笔记已更新。')
                 # Refresh if category changed or title changed
                 if category_id_to_save != self.current_category.id:
                      self.load_notes_for_category(self.current_category.id)
                      self.clear_editor()
                      self.set_editor_enabled(False)
                 else:
                      self.current_note.title = title # Update title in list item too if possible
                      self.note_list.currentItem().setText(title)
            else:
                 QMessageBox.warning(self, '错误', '更新笔记失败。')
        else: # Add new note
            new_note = self.note_manager.add_note(title, content, category_id_to_save)
            if new_note:
                QMessageBox.information(self, '成功', '笔记已添加。')
                # If added to current category, refresh list and select it
                if category_id_to_save == self.current_category.id:
                     self.load_notes_for_category(self.current_category.id)
                     # Find and select the newly added note
                     for i in range(self.note_list.count()):
                          item = self.note_list.item(i)
                          if item.data(Qt.UserRole).id == new_note.id:
                               self.note_list.setCurrentItem(item)
                               break
                else: # If added to different category via combo, just clear editor
                    self.clear_editor()
                    self.set_editor_enabled(False)
                    
            else:
                QMessageBox.warning(self, '错误', '添加笔记失败。')

    def delete_note(self):
        """Deletes the selected note."""
        if not self.current_note:
            QMessageBox.warning(self, '警告', '请先选择要删除的笔记。')
            return

        reply = QMessageBox.question(self, '确认删除', 
                                   f'确定要删除笔记 "{self.current_note.title}" 吗？',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.note_manager.delete_note(self.current_note.id):
                QMessageBox.information(self, '成功', '笔记已删除。')
                # Refresh note list for the current category
                self.load_notes_for_category(self.current_category.id) 
                self.clear_editor()
                self.set_editor_enabled(False)
            else:
                QMessageBox.warning(self, '错误', '删除笔记失败。')

    def search_notes(self):
        """Filters the notes list based on search input *within the current category*."""
        # This function should only be active when NOT in global search mode
        if self.global_search_input.text() or not self.current_category: 
             return 
        
        keyword = self.search_input.text().strip()
        self.clear_note_list()
        
        # Use the category-specific search
        notes = self.note_manager.search_notes(keyword, self.current_category.id)
        for note in notes:
            item = QListWidgetItem(note.title) # Only title needed here
            item.setData(Qt.UserRole, note)
            self.note_list.addItem(item)
            
        self.current_note = None # Deselect note after search
        self.clear_editor()
        self.set_editor_enabled(False)

    # --- UI Utility Methods ---    
    def clear_editor(self):
        """Clears the title and content fields."""
        self.title_input.clear()
        self.content_input.clear()
        self.move_category_combo.setCurrentIndex(-1) # Reset combo

    def clear_note_list(self):
         self.note_list.clear()

    def set_editor_enabled(self, enabled: bool):
        """Enables or disables editor fields and buttons."""
        self.title_input.setEnabled(enabled)
        self.content_input.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled and self.current_note is not None)
        self.move_category_combo.setEnabled(enabled and self.current_note is not None)

def main():
    app = QApplication(sys.argv)
    # Apply a style (optional, Fusion usually looks good cross-platform)
    # app.setStyle(QStyleFactory.create('Fusion')) 
    window = NoteApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 