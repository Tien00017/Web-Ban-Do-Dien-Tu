from flask import Flask, request, jsonify

app = Flask(__name__)

# Fake database
products = []
current_id = 1

# CREATE product
@app.route('/products', methods=['POST'])
def create_product():
    global current_id
    data = request.json
    data['id'] = current_id
    current_id += 1
    products.append(data)
    return jsonify({"message": "Product created", "product": data}), 201

# UPDATE product
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    for p in products:
        if p['id'] == product_id:
            p.update(data)
            return jsonify({"message": "Product updated", "product": p})
    return jsonify({"error": "Product not found"}), 404

# DELETE product
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    for p in products:
        if p['id'] == product_id:
            products.remove(p)
            return jsonify({"message": "Product deleted"})
    return jsonify({"error": "Product not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
