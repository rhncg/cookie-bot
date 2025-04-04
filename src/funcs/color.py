from funcs.data import get_data, update_data

async def get_color(data):
    try:
        color = data['options']['profile_color']
    except KeyError:
        color = "default"
        data['options']['profile_color'] = color
        await update_data(data)
    
    if color == "default":
        color = 0x6b4f37

    if isinstance(color, str) and color.startswith("#"):
        color = int("0x" + color[1:], 16)
        
    return color