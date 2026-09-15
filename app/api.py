import json
import re
from flask import Blueprint, request, jsonify
from .database import get_db
from .pricing import calculate

api = Blueprint('api', __name__, url_prefix='/api')

def body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError('Ожидается JSON-объект.')
    return data

@api.errorhandler(ValueError)
def invalid(error):
    return jsonify(error=str(error)), 400

@api.post('/calculate')
def calculate_api():
    return jsonify(calculate(body()))

@api.post('/contact')
def contact():
    data = body()
    values = {}
    for key, minimum, maximum in [('name', 2, 80), ('contact', 5, 100), ('car_model', 2, 120), ('message', 0, 2000)]:
        value = data.get(key, '')
        if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum or any(ord(c) < 32 and c not in '\n\r\t' for c in value):
            raise ValueError(f'Проверьте поле {key}: от {minimum} до {maximum} символов.')
        values[key] = value.strip()
    contact_value = values['contact']
    telegram_valid = re.fullmatch(r'@[A-Za-z][A-Za-z0-9_]{3,31}', contact_value)
    phone_valid = (re.fullmatch(r'\+?[0-9 ()\-]{7,25}', contact_value)
                   and 7 <= sum(c.isdigit() for c in contact_value) <= 15)
    if not (telegram_valid or phone_valid):
        raise ValueError('Укажите телефон или Telegram в формате @username.')
    if data.get('consent') is not True:
        raise ValueError('Подтвердите согласие на сохранение заявки.')
    config = calculate(data.get('configuration'))
    cart = data.get('cart', [])
    if not isinstance(cart, list) or len(cart) > 30:
        raise ValueError('В корзине может быть не более 30 позиций.')
    items = [calculate(item) for item in cart]
    total = sum(item['total'] for item in items) if items else config['total']
    db = get_db()
    cursor = db.execute('INSERT INTO leads (name, contact, car_model, message, configuration, cart, total) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (*values.values(), json.dumps(config, ensure_ascii=False), json.dumps(items, ensure_ascii=False), total))
    db.commit()
    return jsonify(id=cursor.lastrowid, total=total, message='Заявка сохранена локально. Это учебный проект: звонок менеджера не ожидается.'), 201
