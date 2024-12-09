from datetime import datetime

print(datetime.now().date())
# Example current_date string
current_date_str = "Mon, 09 Dec 2024 00:00:00 GMT"

# Convert string to datetime object
current_date = datetime.strptime(current_date_str, "%a, %d %b %Y %H:%M:%S GMT")

# Format the datetime object to the desired format: 'YYYY-MM-DD'
formatted_date = current_date.strftime("%Y-%m-%d")

# print(formatted_date)  # Output: 2024-12-09