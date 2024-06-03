from flask import Flask,request, jsonify,abort
from random import choice

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
 
about_me = {
    "name": "Александр",
    "surname": "Ситников",
}

quotes = [
   {
        "id": 3,
        "author": "Rick Cook",
        "rating":1,
        "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
   },
   {
        "id": 5,
        "author": "Waldi Ravens",
        "rating":2,
        "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
        "id": 6,
        "author": "Mosher’s Law of Software Engineering",
        "rating":5,
        "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
        "id": 8,
        "author": "Yoggi Berra",
        "rating":1,
        "text": "В теории, теория и практика неразделимы. На практике это не так."
   },

]


@app.route("/")
def hello_world():
    return "Hello, World!"
 

@app.route("/quotes")
def quotes_all():
    return jsonify(quotes)


@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    last_quote = quotes[-1]
    new_id = last_quote['id'] +  1
    new_quote['id'] = new_id
    if new_quote.get("rating") is None or new_quote.get("rating") not in range(1,6):
        new_quote["rating"] = 1
    quotes.append(new_quote)
    return jsonify(new_quote), 201

@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    new_quote = request.json
    for quote in quotes:
        if quote["id"] == quote_id: 
            quote.update(new_quote)
            return jsonify(quote), 200
        abort(404,f"Quote with id={quote_id} not found")
        #return f"Quote with id={quote_id} not found", 404



@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    # Закончить реализацию
    for quote in quotes:
        if quote["id"] == quote_id: 
            quotes.remove(quote)
            return f"Quote with id={quote_id} has deleted {quote}", 200
        abort(404)
        #return f"Quote with id={quote_id} not found", 404
 
@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    for quote in quotes:
        if quote["id"] == quote_id:
            return jsonify(quote), 200
    abort(404,f"Quote with id={quote_id} not found")
    #return f"Quote with id={quote_id} not found", 404


@app.route("/quotes/filter")
def get_quotes_by_filter():
    args = request.args
    print(f' {args = }')
    result = []
    # Закончить реализацию
    for quote in quotes:
        if all(args[key] == str(quote[key]) for key in args):
        #решение с типизацией данных
        #if all(args.get(key, type=type(quote[key])) == quote[key] for key in args): 
            result.append(quote)
    return jsonify(result)


@app.route("/quotes/random", methods=["GET"])
def random_quote():
    return jsonify(choice(quotes))


@app.route("/quotes/count")
def quotes_count():
    return {
        "count":len(quotes)
    }

@app.route("/about")
def about():
    return about_me


if __name__ == "__main__":
    app.run(host='192.168.10.43',debug=True)
  