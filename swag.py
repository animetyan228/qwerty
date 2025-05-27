from flask import Flask, request, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/', methods=['GET'])
def add():
    """
    Сложение двух чисел через GET
    ---
    parameters:
      - name: x
        in: query
        type: integer
        required: true
        description: Первое число
      - name: y
        in: query
        type: integer
        required: true
        description: Второе число
    responses:
      200:
        description: Успешный ответ с суммой
        schema:
          type: object
          properties:
            Сумма GET:
              type: integer
              example: 13
    """
    x = request.args.get('x')
    y = request.args.get('y')

    if x is None or y is None:
        return jsonify({'Ошибка': 'Введите числа'})

    try:
        x = int(x)
        y = int(y)
    except ValueError:
        return jsonify({'Ошибка': 'Введите числа'})

    result = x + y
    return jsonify({'Сумма GET': result})

@app.route('/sum2', methods=['POST'])
def sum2():
    """
    Сложение двух чисел через POST
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: тело запроса
        schema:
          type: object
          required:
            - x
            - y
          properties:
            x:
              type: integer
              description: Первое число
            y:
              type: integer
              description: Второе число
    responses:
      200:
        description: Успешный ответ с суммой
        schema:
          type: object
          properties:
            Сумма POST:
              type: integer
              example: 37
    """
    sun = request.get_json()
    x = sun.get('x')
    y = sun.get('y')

    if x is None or y is None:
        return jsonify({'Ошибка': 'Введите числа'})

    try:
        x = int(x)
        y = int(y)
    except ValueError:
        return jsonify({'Ошибка': 'Введите числа'})

    result = x + y
    return jsonify({'Сумма POST': result})

if __name__ == '__main__':
    app.run(debug=True)

#parameters: — описание входных параметров
#- name: - Имя параметра
#in: query - Где искать (query — значит ?x=1&y=2) consumes: — ожидаемый тип данных
#type:#integer - Тип параметра
#required: true - Обязателен?
#description: Первое число - Подсказка
#responses: — описание ответа
#consumes: — ожидаемый тип данных
#schema: - Структура объекта (тип, поля, пример)

