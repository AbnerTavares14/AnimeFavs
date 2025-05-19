import os
from app.models import Anime
from app import create_app, db
from flask import Flask

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Anime=Anime)

@app.cli.command("init-db")
def init_db():
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado com sucesso.")

if __name__ == '__main__':
    app.run(debug=True)