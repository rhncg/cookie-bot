import math

async def calculate_level(xp):
    return int(math.log10(xp + 1))
    

async def get_xp_bar_data(xp):
    level = await calculate_level(xp)
    current_level_xp = 10 ** level - 1
    next_level_xp = 10 ** (level + 1) - 1
    progress = (xp - current_level_xp) / (next_level_xp - current_level_xp) * 100
    bar = []
    for i in range(1, 11):
        if i * 10 <= round(progress / 10) * 10:
            bar.append("⬜")
        else:
            bar.append("⬛")
    bar.append(f" ({progress:.0f}%)")
    bar = "".join(bar)
    return [current_level_xp, next_level_xp, progress, bar]