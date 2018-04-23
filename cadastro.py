from app import app, db
from app.models import Supplier, Order, Item, OrderItem

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Supplier': Supplier, 'Order': Order, 'Item': Item, 'OrderItem': OrderItem}

if __name__ == "__main__":
    app.run(debug=True)
