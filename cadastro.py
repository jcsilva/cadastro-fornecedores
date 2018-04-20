from app import app, db
from app.models import Provider, Transaction

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Provider': Provider, 'Transaction': Transaction}

if __name__ == "__main__":
    app.run(debug=True)
