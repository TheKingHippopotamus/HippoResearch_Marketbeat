"""
Archive Management Tool
Moves articles older than 2 days to archives folder and tracks operations
"""

import os
import json
import shutil
import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

# Import existing modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tools.logger import setup_logging

class ArchiveManager:
    """Manages article archiving operations"""
    
    def __init__(self):
        self.logger = setup_logging()
        
        # Paths
        self.articles_dir = Path("articles")
        self.archive_dir = Path("/Users/kinghippo/Documents/rssFeed/marketBit_archives/public/archive")
        self.tracking_file = Path("logs-tracker/archive_tracking.json")
        
        # Ensure directories exist
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Archive threshold (2 days = 48 hours from 00:05)
        self.archive_threshold_hours = 48
        
    def get_current_datetime(self) -> datetime.datetime:
        """Get current date and time"""
        return datetime.datetime.now()
    
    def is_file_old_enough(self, file_path: Path) -> bool:
        """
        Check if file is older than 2 days (48 hours from 00:05)
        """
        try:
            # Get file modification time
            file_mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
            current_time = self.get_current_datetime()
            
            # Calculate time difference
            time_diff = current_time - file_mtime
            hours_diff = time_diff.total_seconds() / 3600
            
            self.logger.debug(f"File: {file_path.name}, Age: {hours_diff:.2f} hours")
            
            return hours_diff >= self.archive_threshold_hours
            
        except Exception as e:
            self.logger.error(f"Error checking file age for {file_path}: {e}")
            return False
    
    def load_tracking_data(self) -> Dict[str, Any]:
        """Load existing tracking data from JSON"""
        try:
            if self.tracking_file.exists():
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "archive_sessions": [],
                    "total_files_archived": 0,
                    "last_archive_date": None
                }
        except Exception as e:
            self.logger.error(f"Error loading tracking data: {e}")
            return {
                "archive_sessions": [],
                "total_files_archived": 0,
                "last_archive_date": None
            }
    
    def save_tracking_data(self, data: Dict[str, Any]) -> None:
        """Save tracking data to JSON"""
        try:
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            self.logger.error(f"Error saving tracking data: {e}")
    
    def archive_file(self, file_path: Path) -> bool:
        """Move a single file to archive directory"""
        try:
            # Create archive path
            archive_path = self.archive_dir / file_path.name
            
            # Move file to archive
            shutil.move(str(file_path), str(archive_path))
            
            self.logger.info(f"Archived: {file_path.name} -> {archive_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error archiving {file_path}: {e}")
            return False
    
    def find_old_articles(self) -> List[Path]:
        """Find all articles older than 2 days"""
        old_files = []
        
        if not self.articles_dir.exists():
            self.logger.warning("Articles directory does not exist")
            return old_files
        
        try:
            # Look for HTML files in articles directory
            for file_path in self.articles_dir.glob("*.html"):
                if self.is_file_old_enough(file_path):
                    old_files.append(file_path)
                    
        except Exception as e:
            self.logger.error(f"Error scanning articles directory: {e}")
        
        return old_files
    
    def delete_bak_files(self) -> int:
        """Delete all .bak files in the articles directory"""
        deleted = 0
        for bak_file in self.articles_dir.glob("*.bak"):
            try:
                bak_file.unlink()
                self.logger.info(f"Deleted backup file: {bak_file.name}")
                deleted += 1
            except Exception as e:
                self.logger.error(f"Failed to delete {bak_file.name}: {e}")
        return deleted

    def run_archive_cleanup(self) -> Dict[str, Any]:
        """
        Main archive cleanup operation
        Returns tracking data for this session
        """
        current_time = self.get_current_datetime()
        
        self.logger.info(f"Starting archive cleanup at {current_time}")
        
        # Delete .bak files first
        bak_deleted = self.delete_bak_files()
        if bak_deleted > 0:
            self.logger.info(f"Deleted {bak_deleted} .bak files from articles directory.")
        
        # Find old articles
        old_files = self.find_old_articles()
        
        # Prepare session data
        session_data = {
            "timestamp": current_time.isoformat(),
            "files_found": len(old_files),
            "files_archived": 0,
            "failed_archives": 0,
            "file_details": []
        }
        
        if not old_files:
            self.logger.info("No old articles found to archive")
            session_data["status"] = "no_files_found"
            return session_data
        
        # Archive each old file
        for file_path in old_files:
            file_info = {
                "filename": file_path.name,
                "original_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "modification_time": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            if self.archive_file(file_path):
                session_data["files_archived"] += 1
                file_info["status"] = "archived"
                file_info["archive_path"] = str(self.archive_dir / file_path.name)
            else:
                session_data["failed_archives"] += 1
                file_info["status"] = "failed"
            
            session_data["file_details"].append(file_info)
        
        session_data["status"] = "completed"
        self.logger.info(f"Archive session completed: {session_data['files_archived']} files archived, {session_data['failed_archives']} failed")
        
        return session_data
    
    def update_tracking(self, session_data: Dict[str, Any]) -> None:
        """Update the main tracking file with session data"""
        tracking_data = self.load_tracking_data()
        
        # Add session to history
        tracking_data["archive_sessions"].append(session_data)
        
        # Update totals
        tracking_data["total_files_archived"] += session_data["files_archived"]
        tracking_data["last_archive_date"] = session_data["timestamp"]
        
        # Keep only last 50 sessions to prevent file from growing too large
        if len(tracking_data["archive_sessions"]) > 50:
            tracking_data["archive_sessions"] = tracking_data["archive_sessions"][-50:]
        
        # Save updated tracking data
        self.save_tracking_data(tracking_data)
        
        self.logger.info(f"Tracking updated. Total files archived: {tracking_data['total_files_archived']}")

def main():
    """Main function to run archive cleanup"""
    print("🧹 MarketBit Archive Cleanup Tool")
    print("=" * 40)
    
    try:
        # Initialize archive manager
        archive_manager = ArchiveManager()
        
        # Run cleanup
        session_data = archive_manager.run_archive_cleanup()
        
        # Update tracking
        archive_manager.update_tracking(session_data)
        
        # Print results
        print(f"📊 Archive Session Results:")
        print(f"   Files found: {session_data['files_found']}")
        print(f"   Files archived: {session_data['files_archived']}")
        print(f"   Failed archives: {session_data['failed_archives']}")
        print(f"   Status: {session_data['status']}")
        
        if session_data['files_archived'] > 0:
            print(f"✅ Successfully archived {session_data['files_archived']} files")
        elif session_data['files_found'] == 0:
            print("ℹ️  No old articles found to archive")
        else:
            print("⚠️  Some files failed to archive - check logs for details")
            
    except Exception as e:
        print(f"❌ Error during archive cleanup: {e}")
        logging.error(f"Archive cleanup failed: {e}")

if __name__ == "__main__":
    main()