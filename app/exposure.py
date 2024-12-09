import random
from datetime import datetime, timedelta

def exposure_cal(all_ads):
    ads_id = []
    budget_arr = []
    date_arr = []
    current_date = datetime.now().date()
    for data in all_ads:
        start_date = data[4]
        duration = data[5] - 1
        expiration_date = start_date + timedelta(days=duration)

        if current_date <= expiration_date and current_date >= start_date:
            ads_id.append(data[0])
            budget_arr.append(data[2])
        else:
            date_arr.append(f"{expiration_date}, {current_date}, {start_date}")

    budget_total = sum(budget_arr)
    probabilities = [float(budget) / float(budget_total) for budget in budget_arr]

    selected_ad = random.choices(ads_id, weights=probabilities, k=1)[0]

    return selected_ad