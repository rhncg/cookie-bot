from datetime import datetime
from src.funcs.balance import update_balance
from src.funcs.db import get_db_connection
import json

async def get_data(user_id):
    print(user_id)
    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute(
        "SELECT user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions, total_cookies, boost_time, boost_level, steal_ping, boost_speed, options FROM users WHERE user_id = ?",
        (user_id,))
    row = await cursor.fetchone()
    if row is None:
        await cursor.execute(
            "INSERT INTO users (user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions, total_cookies, boost_time, boost_level, steal_ping, boost_speed, options) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, 0, 1, 60, False, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, True, 10, '{"steal_ping": true, "gamble_confirmation": true}'))
        await conn.commit()
        await cursor.execute(
            "SELECT user_id, balance, oven_cap, bake_speed, ping, last_active, idle_upgrade_level, last_daily, xp, last_steal, last_gamble, daily_streak, interactions, total_cookies, boost_time, boost_level, steal_ping, boost_speed, options FROM users WHERE user_id = ?",
            (user_id,))
        row = await cursor.fetchone()

    data = {
        'user_id': row[0],
        'balance': row[1],
        'oven_cap': row[2],
        'bake_speed': row[3],
        'ping': row[4],
        'last_active': row[5],
        'idle_upgrade_level': row[6],
        'last_daily': row[7],
        'xp': row[8],
        'last_steal': row[9],
        'last_gamble': row[10],
        'daily_streak': row[11],
        'interactions': row[12],
        'total_cookies': row[13],
        'boost_time': row[14],
        'boost_level': row[15],
        'steal_ping': row[16],
        'boost_speed': row[17],
        'options': json.loads(row[18])
    }

    data = await update_idle(data)
    
    return data

async def update_data(data):
    data['options'] = json.dumps(data['options'])
    
    user_id = data.pop('user_id', None)
    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
    values = list(data.values())
    values.append(user_id)
    
    if datetime.now().timestamp() - data['last_daily'] > 172800:
        data['daily_streak'] = 0

    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
    await conn.commit()
    
async def update_idle(data):
    if data['last_active'] == 0:
        data['last_active'] = datetime.now().timestamp()
    time_elapsed = (datetime.now().timestamp() - data['last_active']) // 60
    if time_elapsed > 0 and data['idle_upgrade_level'] > 1:
        idle_upgrade = 1.2 ** (data['idle_upgrade_level'] - 1) - 1
        idle_cookies = int(time_elapsed * idle_upgrade)
        data = await update_balance(data, idle_cookies)
        data['last_active'] = datetime.now().timestamp()
    else:
        data['last_active'] = datetime.now().timestamp()
    
    data['interactions'] += 1
    return data

async def get_user_ids():
    conn = await get_db_connection()
    cursor = await conn.cursor()
    await cursor.execute("SELECT user_id FROM users")
    rows = await cursor.fetchall()
    user_ids = [row[0] for row in rows]
    print(user_ids)
    return user_ids