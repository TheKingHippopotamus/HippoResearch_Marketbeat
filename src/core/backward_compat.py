"""
Backward compatibility wrappers
Wrappers לשמירה על תאימות עם הקוד הישן

This module provides wrapper functions that allow the old code to continue working
while gradually transitioning to the new structure.
"""
import sys
import os

# Add src to path for imports
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def wrap_utils_for_old_code():
    """
    Make new utils available with old names for backward compatibility
    הופך את ה-utils החדשים לזמינים עם שמות ישנים
    """
    # This will be imported by old modules that need these functions
    from src.core.utils import (
        get_current_date,
        get_current_timestamp,
        create_safe_filename
    )
    
    # These can be used in old code like:
    # from src.core.backward_compat import get_current_date
    return {
        'get_current_date': get_current_date,
        'get_current_timestamp': get_current_timestamp,
        'create_safe_filename': create_safe_filename,
    }


# Export for easy import
from src.core.utils import get_current_date, get_current_timestamp, create_safe_filename

