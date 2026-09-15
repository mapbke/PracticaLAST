from .pricing import DEFAULT, calculate

def preset(**kwargs):
    return {**DEFAULT, **kwargs}

SERVICES = [
    ('01', 'Custom steering', 'Руль, который хочется держать. Новая анатомия хвата, кожа и точная строчка.', 'wheel', 'leather', 'wheel'),
    ('02', 'Alcantara interior', 'Мягкая фактура, глубокий цвет и спортивное настроение каждого касания.', 'full', 'alcantara', 'seat'),
    ('03', 'Carbon dashboard', 'Выразительное плетение карбона и аккуратная геометрия торпедо.', 'dash', 'carbon_matte', 'dash'),
    ('04', 'Console styling', 'Переосмысление центральной консоли: от поверхности до последнего шва.', 'console', 'leather', 'console'),
    ('05', 'Signature stitching', 'Контрастная строчка и персональная вышивка для вашего руля.', 'wheel', 'alcantara', 'stitch'),
    ('06', 'Full interior rebuild', 'Цельный образ салона: материалы, оттенки и детали в одном ритме.', 'full', 'leather', 'cabin'),
]
SERVICES = [dict(id=i, name=n, description=d, image=im, **calculate(preset(target=t, material=m))) for i,n,d,t,m,im in SERVICES]
PRODUCTS = [dict(name=n, image=im, **{k:v for k,v in calculate(preset(**p)).items()}) for n,im,p in [
    ('Sport Grip / 01', 'wheel', dict(centerMark=True, perforation=True)),
    ('Carbon Signature / 02', 'dash', dict(target='dash', material='carbon_matte')),
    ('Night Cabin / 03', 'seat', dict(target='full', material='alcantara', embroidery=True)),
]]
CASES = [dict(name=n, subtitle=s, image=im, config=preset(target='full', material=m, stitchColor=c)) for n,s,im,m,c in [
    ('GT Midnight', 'Nissan GT-R · ночная спецификация', 'cabin', 'alcantara', 'red'),
    ('A90 / Akai', 'Toyota Supra · красный акцент', 'wheel', 'leather', 'red'),
    ('Rotary Spirit', 'Mazda RX-7 · лёгкость и фактура', 'seat', 'alcantara', 'ivory'),
    ('M4 Graphite', 'BMW M4 · геометрия карбона', 'dash', 'carbon_matte', 'black'),
    ('911 Heritage', 'Porsche 911 · спокойная классика', 'stitch', 'leather', 'ivory'),
    ('AMG Obsidian', 'Mercedes-AMG · тёмный глянец', 'console', 'carbon_gloss', 'black'),
    ('RS6 Touring', 'Audi RS6 · повседневный спорт', 'cabin', 'alcantara', 'purple'),
    ('LC Moonlight', 'Lexus LC · мягкий контраст', 'seat', 'leather', 'ivory'),
]]
FAQ = [
    ('Сколько занимает работа?', 'В концепции ателье небольшие работы занимают 3–7 дней, полный интерьер — 3–6 недель. Это демонстрационные сроки, реальное производство на сайте не ведётся.'),
    ('Можно изменить только руль?', 'Да. Выберите «Руль» в конфигураторе, материал и дополнительные детали. Полный комплект заказывать необязательно.'),
    ('Какие материалы доступны?', 'В конфигураторе доступны натуральная кожа, Alcantara, матовый и глянцевый карбон. Образцы на сайте иллюстративные.'),
    ('Цена в конфигураторе окончательная?', 'Нет. Это ориентировочный серверный расчёт. В реальном заказе стоимость зависит от модели, состояния деталей и сложности работы.'),
    ('Можно сделать индивидуальный дизайн?', 'Опишите цвет, рисунок и идеи в комментарии к заявке. Вышивку можно включить отдельно в конфигураторе.'),
    ('Возможен комплект без установки?', 'Такой вариант предусмотрен концепцией магазина. Укажите пожелание в комментарии; сумма не является офертой.'),
    ('Работаете по фото-референсам?', 'Идею можно описать в комментарии. Загрузка файлов в учебном проекте не предусмотрена.'),
    ('Как сохранить подборку?', 'Корзина автоматически сохраняется в этом браузере. При следующем открытии цены повторно проверяются на сервере.'),
]
