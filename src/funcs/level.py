import math

async def calculate_level(xp):
    return int(math.log(xp + 1) / math.log(1.05))
    

async def get_xp_bar_data(xp):
    level = await calculate_level(xp)
    current_level_xp = 1.05 ** level - 1
    next_level_xp = 1.05 ** (level + 1) - 1
    progress = (xp - current_level_xp) / (next_level_xp - current_level_xp) * 100
    bar = []
    for i in range(1, 11):
        if i * 10 <= round(progress / 10) * 10:
            if i == 1:
                bar.append("<:left_cap_full:1351715389163311185>")
            elif i == 10:
                bar.append("<:right_cap_full:1351715416388407306>")
            else:
                bar.append("<:mid_full:1351715402765566057>")
        else:
            if i == 1:
                bar.append("<:left_cap_empty:1352053631230152765>")
            elif i == 10:
                bar.append("<:right_cap_empty:1352053652222775357>")
            else:
                bar.append("<:mid_empty:1352053641665708083>")

    bar.append(f" ({progress:.0f}%)")
    bar = "".join(bar)
    return [current_level_xp, next_level_xp, progress, bar]