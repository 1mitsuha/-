from typing import List, Optional
from datetime import datetime
from models import Note, Category, Session
from sqlalchemy.exc import IntegrityError

class NoteManager:
    def __init__(self):
        self.session = Session()
        self._ensure_default_category()

    def _ensure_default_category(self):
        """Ensures at least one category exists, e.g., 'Uncategorized'."""
        if not self.get_all_categories():
            self.add_category("Uncategorized")

    # --- Category Management ---
    def add_category(self, name: str) -> Optional[Category]:
        """Adds a new category.
        Returns the new Category object or None if name already exists."""
        if self.session.query(Category).filter(Category.name == name).first():
            return None # Category already exists
        category = Category(name=name)
        self.session.add(category)
        try:
            self.session.commit()
            return category
        except IntegrityError:
            self.session.rollback()
            return None
        
    def get_all_categories(self) -> List[Category]:
        """Returns a list of all categories."""
        return self.session.query(Category).order_by(Category.name).all()
        
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Finds a category by its ID."""
        return self.session.query(Category).filter(Category.id == category_id).first()
        
    def update_category_name(self, category_id: int, new_name: str) -> bool:
        """Updates the name of a category."""
        category = self.get_category_by_id(category_id)
        if category and not self.session.query(Category).filter(Category.name == new_name).first():
            category.name = new_name
            try:
                self.session.commit()
                return True
            except IntegrityError:
                self.session.rollback()
                return False
        return False

    def delete_category(self, category_id: int) -> bool:
        """Deletes a category and all notes within it."""
        category = self.get_category_by_id(category_id)
        if category:
            # Cascade delete should handle notes due to relationship setting
            self.session.delete(category)
            self.session.commit()
            return True
        return False

    # --- Note Management ---
    def add_note(self, title: str, content: str, category_id: int) -> Optional[Note]:
        """Adds a new note to a specific category."""
        category = self.get_category_by_id(category_id)
        if not category:
            return None # Category doesn't exist
            
        note = Note(
            title=title,
            content=content,
            category_id=category_id
        )
        self.session.add(note)
        self.session.commit()
        return note

    def delete_note(self, note_id: int) -> bool:
        """Deletes a note by its ID."""
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if note:
            self.session.delete(note)
            self.session.commit()
            return True
        return False

    def find_note_by_id(self, note_id: int) -> Optional[Note]:
         """Finds a note by its ID."""
         return self.session.query(Note).filter(Note.id == note_id).first()

    def search_notes(self, keyword: str, category_id: Optional[int] = None) -> List[Note]:
        """Searches notes by keyword, optionally within a specific category."""
        query = self.session.query(Note).filter(
            Note.title.like(f'%{keyword}%') | 
            Note.content.like(f'%{keyword}%')
        )
        if category_id:
            query = query.filter(Note.category_id == category_id)
        return query.order_by(Note.updated_at.desc()).all()

    def update_note(self, note_id: int, new_title: str, new_content: str, new_category_id: Optional[int] = None) -> bool:
        """Updates a note's title, content, and optionally category."""
        note = self.find_note_by_id(note_id)
        if note:
            note.title = new_title
            note.content = new_content
            if new_category_id and new_category_id != note.category_id:
                # Check if new category exists
                new_category = self.get_category_by_id(new_category_id)
                if not new_category:
                    return False # Cannot move to non-existent category
                note.category_id = new_category_id
            note.updated_at = datetime.now() # Manually update timestamp
            self.session.commit()
            return True
        return False

    def get_all_notes(self) -> List[Note]:
        """Gets all notes across all categories."""
        return self.session.query(Note).order_by(Note.updated_at.desc()).all()
        
    def get_notes_by_category(self, category_id: int) -> List[Note]:
        """Gets all notes for a specific category ID."""
        return self.session.query(Note).filter(Note.category_id == category_id).order_by(Note.updated_at.desc()).all()

    def search_all_notes(self, keyword: str) -> List[Note]:
        """Searches notes by keyword across ALL categories."""
        if not keyword:
            return [] # Return empty list if keyword is empty
        query = self.session.query(Note).filter(
            Note.title.like(f'%{keyword}%') | 
            Note.content.like(f'%{keyword}%')
        )
        return query.order_by(Note.updated_at.desc()).all()

    def __del__(self):
        self.session.close() 