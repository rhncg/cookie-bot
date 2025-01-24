from datetime import datetime
import math

async def update_balance(data, amount):
    if data['boost_time'] > datetime.now().timestamp() and amount > 0:
        boost_amount = data['boost_level'] * 0.25 + 1
        data['balance'] += math.ceil(amount * boost_amount)
        data['total_cookies'] += math.ceil(amount * boost_amount) 
    else:
        data['balance'] += int(amount)
        if amount > 0:
            data['total_cookies'] += int(amount)

    return data
