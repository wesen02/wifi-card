import psycopg2
from media_converter import database
from datetime import datetime, timedelta

if __name__ == "__main__":
    ads_data = database.read_ads_db()

    for data in ads_data:
        start_date = data[4]
        duration = data[5]
        data_id = data[0]

        expiration_date = start_date + timedelta(days=duration)

        # Get the current date
        current_date = datetime.now().date()
        if expiration_date == current_date:
            print(f"{data_id} advertisement Done")
            database.update_ads(data_id)
