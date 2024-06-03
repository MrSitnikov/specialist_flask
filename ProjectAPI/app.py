from flask import Flask,request, jsonify,abort
from pathlib import Path
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = Path(__file__).parent


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    quotes = db.relationship(
        'QuoteModel', backref='author', cascade="all, delete-orphan", lazy='dynamic')

    def __init__(self, name):
       self.name = name

    def to_dict(self):
        return {
            "id" :self.id,
            "name":self.name,
        }

class QuoteModel(db.Model):
    __tablename__ = "quotes"
    id = db.Column(db.Integer, primary_key=True)
    #author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    #или
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)
    rating = db.Column(db.Integer, nullable=False, default=1)
    
    def __init__(self, author, text, rating=1):
        self.author_id = author.id
        self.text  = text
        self.rating = rating
    
    def to_dict(self):
        return {
            "id" :self.id,
            "author":self.author.to_dict(),
            "text":self.text,
            "rating":self.rating
        }
    
    def __repr__(self):
        return f"QuoteModel{vars(self)}" 


@app.route("/quotes")
def get_quotes_all():
    quotes = QuoteModel.query.all()
    quotes_dict = [i.to_dict() for i in quotes]
    return jsonify(quotes_dict),200


@app.post("/quotes")
def gette_quote():
    new_quote = request.json
    #quote = QuoteModel(new_quote['author'],new_quote['text'],new_quote['rating'])
    quote = QuoteModel(**new_quote)
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


@app.route("/quotes/filter")
def get_quotes_by_filter():
    args = request.args
    l = QuoteModel.query.filter_by(**args).all()
    if l:
        return jsonify([i.to_dict() for i in l]), 200
    abort(404,f"Quote not found")


@app.route("/quotes/<int:quote_id>/rating", methods=['POST'])
def rating_update(quote_id):
    change = request.args.get('value',1)
    quote = QuoteModel.query.get(quote_id)
    if quote:
        status = request.args.get('change')
        if status in 'up':
            rating = quote.rating + change
            quote.rating=rating
            db.session.add(quote)
            db.session.commit()
            return jsonify(quote.to_dict()), 200
    abort(404, f"Quote not found")

@app.route("/authors")
def get_author():
    authors = AuthorModel.query.all()
    authors_dict = [i.to_dict() for i in authors]
    return jsonify(authors_dict), 200


@app.route("/authors/<int:author_id>")
def get_author_by_id(author_id):
    authors = AuthorModel.query.get(author_id)
    if not authors:
        return abort(404,f'Автора с id {author_id} нет')
    return jsonify(authors.to_dict()), 200


@app.route("/authors", methods=["POST"])
def create_author():
       author_data = request.json
       author = AuthorModel(author_data["name"])
       db.session.add(author)
       db.session.commit()
       return jsonify(author.to_dict()), 201


@app.put("/authors/<int:author_id>")
def edit_author(author_id):
    new_quote = request.json
    author = AuthorModel.query.get(author_id)
    if author is None:
        abort(404, f"Quote with id={author_id} not found")
    # if new_quote.get('author'):
    #     quote.author = new_quote['author']
    # if new_quote.get('text'):
    #     quote.text = new_quote['text']
    for k,v in new_quote.items():
        # аналогично author.name = 'New Name'
        setattr(author, k, v)
    db.session.commit()
    return jsonify(author.to_dict()), 200


    
@app.route("/authors/<int:author_id>", methods=["DELETE"])
def delete_author_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        abort(404, f"Author_id with id={author_id} not found")
    db.session.delete(author)
    db.session.commit()
    return f"Quote with id={author_id} has deleted {author.to_dict()}", 200


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_quote(author_id):
    author = AuthorModel.query.get(author_id)
    new_quote = request.json
    q = QuoteModel(author, new_quote["text"])
    db.session.add(q)
    db.session.commit()
    return jsonify(q.to_dict()), 201


if __name__ == "__main__":
    app.run(host='192.168.10.43',debug=True)
  