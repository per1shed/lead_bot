"""функция, которая работает с экранированием символов при маркаудне"""
def escape_sym(text):
    text = text.replace('.', '\\.')
    return text

if __name__ == '__main__':
    print(escape_sym("Привет, . Хочешь гайд?"))