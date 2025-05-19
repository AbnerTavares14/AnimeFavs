import os
from app.models import Anime
from app import create_app, db


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    # db.drop_all()
    db.create_all()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Anime=Anime)



if __name__ == '__main__':
    app.run(debug=True)