from flask import Flask,request, jsonify,abort
from pathlib import Path
import sqlite3
from werkzeug.exceptions import HTTPException

from flask_sqlalchemy import SQLAlchemy

BASE_DIR = Path(__file__).parent


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class QuoteModel(db.Model):
    __tablename__ = "quotes"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(32), unique=False)
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author = author
        self.text  = text
    
    def to_dict(self):
        return {
            "id" :self.id,
            "author":self.author,
            "text":self.text
        }
    
    def __repr__(self):
        return f"QuoteModel{vars(self)}" 



# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


@app.route("/quotes")
def quotes_all():
    quotes = QuoteModel.query.all()
    quotes_dict = [i.to_dict() for i in quotes]
    return jsonify(quotes_dict),200


@app.post("/quotes")
def create_quote():
    new_quote = request.json
    quote = QuoteModel(new_quote['author'],new_quote['text'])
    db.session.add(quote)
    db.session.commit()
    return jsonify(quote.to_dict()), 200


@app.put("/quotes/<int:quote_id>")
def edit_quote(quote_id):
    new_quote = request.json
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404,f"Quote with id={quote_id} not found")
    # if new_quote.get('author'):
    #     quote.author = new_quote['author']
    # if new_quote.get('text'):
    #     quote.text = new_quote['text']
    for k,v in new_quote.items():
        setattr(quote,k,v)
    db.session.commit()
    return jsonify(quote.to_dict()), 200

@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404,f"Quote with id={quote_id} not found")
    db.session.delete(quote)
    db.session.commit()
    return f"Quote with id={quote_id} has deleted {quote.to_dict()}", 200


@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404,f"Quote with id={quote_id} not found")
    return jsonify(quote.to_dict()), 200



if __name__ == "__main__":
    app.run(host='192.168.10.43',debug=True)
  