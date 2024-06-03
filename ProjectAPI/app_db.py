from flask import Flask,request, jsonify,abort,g
from pathlib import Path
import sqlite3

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

BASE_DIR = Path(__name__).parent
DATABASE = BASE_DIR / 'test.db'


from werkzeug.exceptions import HTTPException


# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/quotes")
def quotes_all():
    conn = get_db()
    cursor = conn.cursor()
    select_quotes = "SELECT * FROM quotes"
    cursor.execute(select_quotes)
    quotes_qb = cursor.fetchall()
    keys = ['id','author','text']
    quotes =[]
    for q_db in quotes_qb:
        q_db =dict(zip(keys,q_db))
        quotes.append(q_db)
    return jsonify(quotes)


@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    conn = get_db()
    cursor = conn.cursor()
    create_quotes = f"INSERT INTO quotes (author, text) VALUES (?,?)"  
    cursor.execute(create_quotes, (new_quote['author'], new_quote['text']))
    conn.commit()
    new_quote_id = cursor.lastrowid
    new_quote['id'] = new_quote_id
    return jsonify(new_quote), 201

@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    new_quote = request.json
    conn = get_db()
    cursor = conn.cursor()
    select_quotes = f"SELECT * FROM quotes where id = {quote_id}"
    cursor.execute(select_quotes)
    quotes_qb = cursor.fetchone()
    if quotes_qb:
        fields_to_update = ', '.join(f"{k} =?" for k in new_quote.keys())
        update = f"update quotes set {fields_to_update} where id = ?"
        cursor.execute(update, ( *new_quote.values() , quote_id))
        conn.commit()
        return jsonify(new_quote), 200
    abort(404,f"Quote with id={quote_id} not found")



@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    conn = get_db()
    cursor = conn.cursor()
    select_quotes = f"SELECT * FROM quotes where id = {quote_id}"
    cursor.execute(select_quotes)
    quotes_qb = cursor.fetchone()
    if quotes_qb:
        del_quotes = f"delete FROM quotes where id = {quote_id}"
        cursor.execute(del_quotes)
        conn.commit()
        return f"Quote with id={quote_id} has deleted {quotes_qb}", 200
    abort(404,f"Quote with id={quote_id} not found")

 
@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    conn = get_db()
    cursor = conn.cursor()
    select_quotes = f"SELECT * FROM quotes where id={quote_id}"
    cursor.execute(select_quotes)
    quotes_qb = cursor.fetchone()
    if quotes_qb:
        keys = ['id','author','text']        
        quotes = dict(zip(keys,quotes_qb))
        return jsonify(quotes), 200
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


if __name__ == "__main__":
    app.run(host='192.168.10.43',debug=True)
  