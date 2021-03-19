from datetime import datetime, timezone

def cache_bust():
    current_time = datetime.now(timezone.utc)
    bust = "?v=" + str(current_time.year) + "_" + str(current_time.month) + "_" + str(current_time.day)
    return bust
