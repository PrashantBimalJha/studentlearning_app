import logging
import sys
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for different log levels"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    
    def format(self, record):
        # Get the original formatted message
        log_message = super().format(record)
        
        # Add color based on log level
        color = self.COLORS.get(record.levelname, '')
        return f"{color}{log_message}{Style.RESET_ALL}"

def setup_logger(name="LearningApp", level=logging.INFO):
    """Setup a colored logger for the Learning App"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_startup():
    """Log startup banner for Learning App"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}🎓 LEARNING APP - Student Learning Platform 🎓")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}Starting application...")
    print(f"{Fore.CYAN}{'='*60}\n")

def log_success(message):
    """Log success message in green"""
    print(f"{Fore.GREEN}✅ {message}")

def log_error(message):
    """Log error message in red"""
    print(f"{Fore.RED}❌ {message}")

def log_warning(message):
    """Log warning message in yellow"""
    print(f"{Fore.YELLOW}⚠️  {message}")

def log_info(message):
    """Log info message in blue"""
    print(f"{Fore.BLUE}ℹ️  {message}")
