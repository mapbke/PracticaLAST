"""All amounts are integer rubles; client prices are never accepted."""
CARS = {'sedan': ('Седан', 100), 'coupe': ('Купе', 110), 'suv': ('SUV', 125), 'sport': ('Спорткар', 120)}
TARGETS = {'wheel': ('Руль', 28000), 'dash': ('Торпедо', 65000), 'console': ('Консоль', 32000), 'full': ('Полный салон', 210000)}
MATERIALS = {'leather': ('Натуральная кожа', 0), 'alcantara': ('Alcantara', 9000), 'carbon_matte': ('Матовый карбон', 18000), 'carbon_gloss': ('Глянцевый карбон', 22000)}
EXTRAS = {'centerMark': ('Центральная метка', 2500), 'carbonInserts': ('Карбоновые вставки', 12000), 'perforation': ('Перфорация', 4000), 'embroidery': ('Персональная вышивка', 5500)}
STITCHES = {'red': 'Красная', 'ivory': 'Слоновая кость', 'black': 'Чёрная', 'purple': 'Фиолетовая'}
DEFAULT = dict(carType='coupe', target='wheel', material='leather', stitchColor='red', quantity=1, **{k: False for k in EXTRAS})

def calculate(data):
    if not isinstance(data, dict):
        raise ValueError('Конфигурация должна быть объектом.')
    config = {}
    for key, choices in [('carType', CARS), ('target', TARGETS), ('material', MATERIALS), ('stitchColor', STITCHES)]:
        value = data.get(key)
        if not isinstance(value, str) or value not in choices:
            raise ValueError(f'Недопустимое значение: {key}.')
        config[key] = value
    qty = data.get('quantity', 1)
    if type(qty) is not int or not 1 <= qty <= 20:
        raise ValueError('Количество должно быть целым числом от 1 до 20.')
    config['quantity'] = qty
    for key in EXTRAS:
        value = data.get(key, False)
        if type(value) is not bool:
            raise ValueError(f'Параметр {key} должен быть логическим.')
        config[key] = value
    base = TARGETS[config['target']][1] + MATERIALS[config['material']][1]
    unit = base * CARS[config['carType']][1] // 100 + sum(cost for key, (_, cost) in EXTRAS.items() if config[key])
    title = f"{TARGETS[config['target']][0]} · {MATERIALS[config['material']][0]}"
    return dict(config=config, title=title, unitPrice=unit, total=unit * qty, currency='RUB')
