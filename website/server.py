from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, bindparam
from werkzeug.utils import secure_filename
import os
from pathlib import Path

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mainuser:1234@192.168.50.117:3306/test?charset=utf8mb4'
db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = 'goods'
    good_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    img = db.Column(db.String(500), default='')
    popularity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0)

@app.route('/')
def index():
    return render_template('index.html')

# отдельная функция для админа без лимита
@app.route('/api/popular-products', methods=['GET'])
def get_popular_products():
    products = Product.query.order_by(Product.popularity.desc()).limit(10).all()
    return jsonify([{
        'id': p.good_id,
        'name': p.name,
        'description': p.description,
        'img': p.img,
        'price': p.price
    } for p in products])

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.order_by(Product.good_id.desc()).all()
    return jsonify([{
        'id': p.good_id,
        'name': p.name,
        'description': p.description,
        'img': p.img,
        'price': p.price
    } for p in products])

@app.route('/admin')
def render_admin():
    return render_template('admin/index.html')

@app.route('/api/product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        form = request.form
        file = request.files['img']
        image_dir = Path(__file__).resolve().parent / 'static/goods_images'
        if not os.path.exists(image_dir): os.makedirs(image_dir)
        if file:
            filename = secure_filename(file.filename)
            file_path = image_dir / filename
            file.save(file_path)
        query = text("INSERT INTO goods (name, description, img, price) VALUES (:name, :description, :img, :price)")
        query = query.bindparams(
            name=form.get('name'),
            description=form.get('description'),
            img=filename,
            price=form.get('price')
        )
        with db.engine.connect() as connection:
            result = connection.execute(query)
            connection.commit()
        return jsonify(form)

@app.route('/api/product/<int:good_id>', methods=['DELETE'])
def delete_product(good_id):
    product = Product.query.get(good_id)
    if product is None:
        return jsonify({'error': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200

def main():
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            db.session.add(Product(name='Лопата', description='ей копать', popularity=10, img='shawel.jpg', price=12.3))
            db.session.add(Product(name='Компьютер', description='купите ему компьютер, хуле он как дурак', popularity=5, img='pc.jpg', price=43.1))
            db.session.add(Product(name='Телефон', description='ты куда звОнишь', popularity=20, img='phone.jpg', price=14.4))
            db.session.commit()
    app.run("localhost", 8000, debug=True)

if __name__ == '__main__':
    main()