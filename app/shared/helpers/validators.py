from datetime import datetime
from typing import Optional

def format_datetime(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.strftime('%Y-%m-%d %H:%M:%S')
