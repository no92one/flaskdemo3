from flask import Flask, jsonify, request
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker

url = URL.create(
    drivername="postgresql+psycopg2",
    host="localhost",
    port="5544",
    username="postgres",
    password="abc123",
    database="flask_demo"
)

engine = create_engine(url)

app = Flask(__name__)
Session = sessionmaker(bind=engine)

@app.get('/users')
def get_users():
    with Session() as session:
        result = session.execute(text("SELECT * FROM users")).fetchall()
        users_list = [
            {
                "id": row.id,
                "name": row.name,
                "email": row.email
            } for row in result
        ]

    return jsonify(users_list), 200

@app.get('/products')
def get_products():
    with Session() as session:
        result = session.execute(text("SELECT * FROM product")).fetchall()
        products_list = [
            {
                "id": row.id,
                "name": row.name,
                "price": row.price,
                "stock": row.stock
            } for row in result
        ]

    return jsonify(products_list), 200

@app.get('/products/<int:product_id>')
def det_product(product_id):
    with Session() as session:
        result = session.execute(
            text("SELECT * FROM product WHERE id = :id"),
            {"id": product_id}
        ).fetchone()

        if not result:
            return jsonify({"message": f"No product found with id {product_id}."}), 404

        product = {
            "id": result.id,
            "name": result.name,
            "price": result.price,
            "stock": result.stock
        }

    return jsonify(product), 200

@app.post('/products')
def create_product():
    with Session() as session:
        data = request.get_json()
        name = data.get("name")
        price = data.get("price")
        stock = data.get("stock")

        if not name or not price or not stock:
            return jsonify({"message": "Please provide all required fields."}), 400

        result = session.execute(text("""INSERT INTO product (name, price, stock) 
                                          VALUES (:name, :price, :stock) RETURNING *
                                       """),
                                  {"name": name, "price": price, "stock": stock})
        new_product = result.mappings().first()
        print(new_product)
        session.commit()

    return jsonify({
        "message": f"Product '{name}' was created successfully.",
        "product": dict(new_product)
    }), 201

@app.delete('/products/<int:product_id>')
def delete_product(product_id):
    with Session() as session:
        session.execute(text("DELETE FROM product WHERE id = :id"),
                        {"id": product_id})
        session.commit()

    return jsonify({"message": f"Product with id {product_id} was deleted."}), 201

