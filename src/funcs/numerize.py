def numerize(value, decimals=2):
    suffixes = ['', 'K', 'M', 'B', 'T', 'Qu', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'De']
    num = float(value)
    index = 0
    
    while abs(num) >= 1000 and index < len(suffixes) - 1:
        num /= 1000.0
        index += 1
    
    formatted_num = f"{num:.{decimals}f}".rstrip('0').rstrip('.')
    return f"{formatted_num}{suffixes[index]}"