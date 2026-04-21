from datetime import datetime
from zoneinfo import ZoneInfo


def test_get_time():
    tz = ZoneInfo("America/New_York")
    now = datetime.now(tz)
    time_str = now.strftime("%#I:%M %p")
    print(f"Current time (America/New_York): {time_str}")
    print(f"Full timestamp: {now.isoformat()}")
    print("\nPASS")


if __name__ == "__main__":
    test_get_time()
