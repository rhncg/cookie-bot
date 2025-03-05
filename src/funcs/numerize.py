def numerize(value):
    suffixes = ['', 'K', 'M', 'B', 'T', 'Qu', 'Qi', 'Sx']
    num = float(value)
    index = 0
    
    while abs(num) >= 1000 and index < len(suffixes) - 1:
        num /= 1000.0
        index += 1
    
    return f"{num:.2f}{suffixes[index]}"