from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///samba.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    popularity = db.Column(db.Integer, default=0)
    image_name = db.Column(db.String(500), default='')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/popular-products', methods=['GET'])
def get_popular_products():
    products = Product.query.order_by(Product.popularity.desc()).limit(10).all()
    return jsonify([{'id': p.id, 'name': p.name, 'image_name': p.image_name} for p in products])

def main():
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            db.session.add(Product(name='Лопата', popularity=10, image_name='shawel.jpg'))
            db.session.add(Product(name='Компьютер', popularity=5, image_name='pc.jpg'))
            db.session.add(Product(name='Телефон', popularity=20, image_name='phone.jpg'))
            db.session.commit()
    app.run("localhost", 8000, debug=True)

if __name__ == '__main__':
    main()