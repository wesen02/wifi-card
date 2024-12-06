import psycopg2
from database import read_ads_db, update_ads
from datetime import datetime, timedelta

if __name__ == "__main__":
    ads_data = read_ads_db()

    for data in ads_data:
        start_date = data[4]
        duration = data[5] - 1
        data_id = data[0]

        expiration_date = start_date + timedelta(days=duration)

        # Get the current date
        current_date = datetime.now()
        if expiration_date.date() == current_date.date():
            update_ads(data_id)