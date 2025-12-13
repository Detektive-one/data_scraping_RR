"""
Checkpoint management for resumable scraping.
Saves and loads scraping progress to allow pause/resume functionality.
"""
import json
import os
from config import CHECKPOINT_FILE


class Checkpoint:
    """Manages scraping progress checkpoints"""
    
    def __init__(self, filepath=CHECKPOINT_FILE):
        self.filepath = filepath
        self.data = {
            "current_page": 1,
            "total_scraped": 0,
            "last_fiction_id": None,
            "timestamp": None
        }
        self.load()
    
    def load(self):
        """Load checkpoint from file if it exists"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data)
                    print(f"✓ Loaded checkpoint: Page {self.data['current_page']}, "
                          f"{self.data['total_scraped']} novels scraped")
                    return True
            except Exception as e:
                print(f"⚠ Warning: Could not load checkpoint: {e}")
                return False
        return False
    
    def save(self, current_page, total_scraped, last_fiction_id=None):
        """
        Save current progress to checkpoint file.
        
        Args:
            current_page (int): Current page number being scraped
            total_scraped (int): Total number of novels scraped so far
            last_fiction_id (int): ID of the last fiction scraped (optional)
        """
        from datetime import datetime
        
        self.data = {
            "current_page": current_page,
            "total_scraped": total_scraped,
            "last_fiction_id": last_fiction_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"⚠ Warning: Could not save checkpoint: {e}")
    
    def get_start_page(self):
        """Get the page number to start/resume from"""
        return self.data.get("current_page", 1)
    
    def get_total_scraped(self):
        """Get the total number of novels scraped so far"""
        return self.data.get("total_scraped", 0)
    
    def clear(self):
        """Clear the checkpoint file"""
        if os.path.exists(self.filepath):
            try:
                os.remove(self.filepath)
                print("✓ Checkpoint cleared")
            except Exception as e:
                print(f"⚠ Warning: Could not clear checkpoint: {e}")
        self.data = {
            "current_page": 1,
            "total_scraped": 0,
            "last_fiction_id": None,
            "timestamp": None
        }
    
    def __repr__(self):
        return f"Checkpoint(page={self.data['current_page']}, scraped={self.data['total_scraped']})"
