
from datetime import time
from django.utils import timezone


def _norm(name: str) -> str:
    """
    Converts 'breakfast', 'BreakFast', 'DINNER' → 'Breakfast', 'Dinner'
    """
    return name.strip().lower().capitalize()

WINDOWS = {
    "Breakfast": {
        "today":    (time(0, 0, 0),  time(0, 0, 1)),      
        "tomorrow": (time(11, 0), time(23, 59)),    
    },
    "Lunch": {
        "today":    (time(0, 0),  time(9, 0)),     
        "tomorrow": (time(17, 0), time(23, 59)),     
    },
    "Dinner": {
        "today":    (time(0, 0),  time(16, 0)),     
        "tomorrow": (time(22, 0), time(23, 59)),     
    },
}

def is_window_open(meal_name, which_day):
    """
    `which_day` = "today" or "tomorrow"
    Returns True if *now* is inside the allowed booking window.
    """
    meal_name = _norm(meal_name)
    if meal_name not in WINDOWS or which_day not in WINDOWS[meal_name]:
        return False

    start, end = WINDOWS[meal_name][which_day]
    now = timezone.localtime().time()

    
    return start <= now <= end

SHOW_CUTOFF_TIMES = {
    "Breakfast": [time(0, 0, 1), time(9, 30, 0)],
    "Lunch":     [time(9, 0),    time(14, 30)],
    "Dinner":    [time(16, 0),   time(21, 30)]
}

def is_qr_visible_for_meal(meal_name):
    """
    Returns True if the current time is within the QR visibility window
    for the given meal slot.
    """
    meal_name = _norm(meal_name)
    if meal_name not in SHOW_CUTOFF_TIMES:
        raise KeyError(f"{meal_name} is not a valid meal name.")
    
    now = timezone.localtime().time()
    start, end = SHOW_CUTOFF_TIMES[meal_name]
    return start <= now <= end


