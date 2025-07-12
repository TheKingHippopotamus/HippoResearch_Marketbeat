import logging
import functools
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

def setup_logging():
    """Setup logging configuration with script/function/line and color support"""
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
                if any(x in msg for x in ["[STAGE]", "[DONE]", "[SUCCESS]", "[HTML_GEN]", "[JS_INJECT]", "[GIT]", "[META]"]):
                    return color_log(msg, LogColors.OKCYAN)
                elif "[SCRAPE]" in msg or "[TEXT_PREPROCESS]" in msg:
                    return color_log(msg, LogColors.OKBLUE)
                elif "[LLM]" in msg:
                    return color_log(msg, LogColors.OKGREEN)
                else:
                    return msg
            return msg
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] %(message)s',
        handlers=[
            logging.FileHandler('marketbit.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    for handler in logging.getLogger().handlers:
        handler.setFormatter(ColorFormatter('%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'))
    return logging.getLogger(__name__)




    # Add a decorator to log function entry/exit for major steps
def log_stage(stage):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ticker = None
            if 'ticker' in kwargs:
                ticker = kwargs['ticker']
            elif args:
                # Try to infer ticker from first arg if it's a string
                if isinstance(args[0], str):
                    ticker = args[0]
            # Get logger instance
            log = logging.getLogger(__name__)
            log.info(f"[STAGE] {stage} START {'['+ticker+']' if ticker else ''}")
            result = func(*args, **kwargs)
            log.info(f"[STAGE] {stage} END {'['+ticker+']' if ticker else ''}")
            return result
        return wrapper
    return decorator