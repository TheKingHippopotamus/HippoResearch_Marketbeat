import logging
import functools
import os
import threading
from datetime import datetime
import shutil

# ANSI color codes for log highlighting
class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GREY = '\033[90m'
    WHITE = '\033[97m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'

# Helper for colored log messages
def color_log(msg, color):
    return f"{color}{msg}{LogColors.ENDC}"

class DailyLogManager:
    """Manages daily log files with automatic archiving"""
    
    def __init__(self, logs_dir='logs-tracker', max_lines=1000):
        self.logs_dir = logs_dir
        self.archives_dir = os.path.join(logs_dir, 'archives')
        self.max_lines = max_lines
        self.lock = threading.Lock()
        self.current_date = None
        self.current_log_file = None
        self.line_count = 0
        
        # Ensure directories exist
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.archives_dir, exist_ok=True)
        
        self._init_daily_log()
    
    def _get_log_filename(self, date_obj=None):
        """Get log filename for a specific date"""
        if date_obj is None:
            date_obj = datetime.now()
        return f"application{date_obj.strftime('%Y%m%d')}.log"
    
    def _init_daily_log(self):
        """Initialize daily log file"""
        today = datetime.now()
        today_str = today.strftime('%Y%m%d')
        
        # Check if we need to switch to a new day
        if self.current_date != today_str:
            # Archive previous day's log if it exists
            if self.current_log_file and os.path.exists(self.current_log_file):
                self._archive_previous_log()
            
            # Set up new day's log
            self.current_date = today_str
            self.current_log_file = os.path.join(self.logs_dir, self._get_log_filename(today))
            
            # Initialize new log file
            if self.current_log_file and not os.path.exists(self.current_log_file):
                with open(self.current_log_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== Application Log Started: {today.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                self.line_count = 1
            elif self.current_log_file:
                # Count existing lines
                try:
                    with open(self.current_log_file, 'r', encoding='utf-8') as f:
                        self.line_count = sum(1 for _ in f)
                except:
                    self.line_count = 0
    
    def _archive_previous_log(self):
        """Archive the previous day's log file"""
        if not self.current_log_file or not os.path.exists(self.current_log_file):
            return
        
        try:
            # Get yesterday's date
            yesterday = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday = yesterday.replace(day=yesterday.day - 1)
            archive_filename = self._get_log_filename(yesterday)
            archive_path = os.path.join(self.archives_dir, archive_filename)
            
            # Move to archives
            shutil.move(self.current_log_file, archive_path)
            print(f"📦 Archived log: {archive_filename}")
            
        except Exception as e:
            print(f"❌ Error archiving log: {e}")
    
    def _rotate_log(self):
        """Rotate log file when it exceeds max_lines"""
        if self.line_count >= self.max_lines and self.current_log_file:
            try:
                # Read all lines
                with open(self.current_log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Keep only the most recent 200 lines (leaving room for new entries)
                recent_lines = lines[-200:] if len(lines) > 200 else lines
                
                # Add rotation header
                rotation_header = f"\n=== LOG ROTATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
                recent_lines.insert(0, rotation_header)
                
                # Write back to file
                with open(self.current_log_file, 'w', encoding='utf-8') as f:
                    f.writelines(recent_lines)
                
                self.line_count = len(recent_lines)
                if self.current_log_file:
                    print(f"🔄 Log rotated: {os.path.basename(self.current_log_file)} (kept {self.line_count} most recent lines)")
                
            except Exception as e:
                print(f"❌ Error rotating log: {e}")
    
    def write_log(self, message):
        """Write message to current daily log with automatic management"""
        with self.lock:
            try:
                # Check if we need to switch to a new day
                self._init_daily_log()
                
                # Check if rotation is needed
                self._rotate_log()
                
                # Write the message
                if self.current_log_file:
                    with open(self.current_log_file, 'a', encoding='utf-8') as f:
                        f.write(message + '\n')
                    
                    self.line_count += 1
                    
            except Exception as e:
                print(f"❌ Error writing to log: {e}")
    
    def get_current_log_file(self):
        """Get the current log file path"""
        self._init_daily_log()
        return self.current_log_file
    
    def show_status(self):
        """Show log file status"""
        try:
            self._init_daily_log()
            file_size = 0
            if self.current_log_file and os.path.exists(self.current_log_file):
                file_size = os.path.getsize(self.current_log_file)
            
            print(f"📊 Daily Log Status:")
            if self.current_log_file:
                print(f"   📁 Current Log: {os.path.basename(self.current_log_file)}")
            else:
                print(f"   📁 Current Log: None")
            print(f"   📏 Size: {file_size:,} bytes")
            print(f"   📝 Lines: {self.line_count}")
            print(f"   🔄 Max Lines: {self.max_lines}")
            print(f"   📊 Usage: {self.line_count}/{self.max_lines} ({(self.line_count/self.max_lines)*100:.1f}%)")
            
            # Count archived logs
            archived_count = len([f for f in os.listdir(self.archives_dir) if f.endswith('.log')])
            print(f"   📦 Archived Logs: {archived_count}")
            
            if self.current_log_file and os.path.exists(self.current_log_file):
                with open(self.current_log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"   🕒 Last Entry: {lines[-1].strip()}")
                        print(f"   🕒 First Entry: {lines[0].strip()}")
        except Exception as e:
            print(f"❌ Error showing log status: {e}")

# Global daily log manager instance
daily_log_manager = DailyLogManager()

def setup_logging(use_daily_log=True):
    """Setup logging configuration with daily log management"""
    class ColorFormatter(logging.Formatter):
        def format(self, record):
            msg = super().format(record)
            # Color by level
            if record.levelno >= logging.ERROR:
                return color_log(msg, LogColors.FAIL)
            elif record.levelno == logging.WARNING:
                return color_log(msg, LogColors.WARNING)
            elif record.levelno == logging.INFO:
                # Highlight stage starts/ends
                if any(x in msg for x in ["[STAGE]", "[DONE]", "[SUCCESS]", "[HTML_GEN]", "[JS_INJECT]", "[GIT]", "[META]", "[CLEANER]", "[STRUCTURE]", "[PROCESS_ALL]", "[MONITOR]"]):
                    return color_log(msg, LogColors.OKCYAN)
                elif "[SCRAPE]" in msg or "[TEXT_PREPROCESS]" in msg or "[CLEANER]" in msg:
                    return color_log(msg, LogColors.OKBLUE)
                elif "[LLM]" in msg:
                    return color_log(msg, LogColors.OKGREEN)
                else:
                    return msg
            return msg

    # Custom file handler that uses our daily log manager
    class DailyFileHandler(logging.FileHandler):
        def emit(self, record):
            try:
                msg = self.format(record)
                if use_daily_log:
                    daily_log_manager.write_log(msg)
                else:
                    super().emit(record)
            except Exception:
                self.handleError(record)

    # Remove any existing handlers
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Set up handlers
    if use_daily_log:
        current_log_file = daily_log_manager.get_current_log_file()
        if current_log_file:
            file_handler = DailyFileHandler(current_log_file, encoding='utf-8')
        else:
            file_handler = logging.FileHandler('marketbit.log', encoding='utf-8')
    else:
        file_handler = logging.FileHandler('marketbit.log', encoding='utf-8')
    
    stream_handler = logging.StreamHandler()
    handlers = [file_handler, stream_handler]

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] %(message)s',
        handlers=handlers
    )

    # Set formatters: color only for stream, plain for file
    plain_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] %(message)s')
    color_formatter = ColorFormatter('%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] %(message)s')
    file_handler.setFormatter(plain_formatter)
    stream_handler.setFormatter(color_formatter)

    return logging.getLogger(__name__)

# Add a decorator to log function entry/exit for major steps
def log_stage(stage):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ticker = None
            filename = None
            
            # Try to get ticker or filename from kwargs or args
            if 'ticker' in kwargs:
                ticker = kwargs['ticker']
            elif 'file_path' in kwargs:
                filename = kwargs['file_path']
            elif args:
                # Try to infer ticker/filename from first arg if it's a string
                if isinstance(args[0], str):
                    if args[0].endswith('.html') or '/' in args[0]:
                        filename = args[0]
                    else:
                        ticker = args[0]
            
            # Get logger instance
            log = logging.getLogger(__name__)
            identifier = f"[{ticker}]" if ticker else f"[{filename}]" if filename else ""
            log.info(f"[STAGE] {stage} START {identifier}")
            result = func(*args, **kwargs)
            log.info(f"[STAGE] {stage} END {identifier}")
            return result
        return wrapper
    return decorator