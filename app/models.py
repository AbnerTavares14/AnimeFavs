from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from . import login_manager
from flask import current_app
import hashlib
from flask_login import UserMixin, AnonymousUserMixin
import datetime, hashlib

class Anime(db.Model):
    __tablename__ = 'animes'
    id = db.Column(db.Integer, primary_key=True)
    mal_id = db.Column(db.Integer)
    title = db.Column(db.String, unique=True, nullable=False)
    source = db.Column(db.String)
    episodes = db.Column(db.Integer)
    status = db.Column(db.String)
    rating = db.Column(db.String)
    image = db.Column(db.String)
    url = db.Column(db.String)
    synopsis = db.Column(db.Text)
    background = db.Column(db.Text)
    season = db.Column(db.String)
    year = db.Column(db.Integer)
    genres = db.Column(db.String) 


    def to_dict(self):
        return {
            'mal_id': self.mal_id,
            'title': self.title,
            'source': self.source,
            'episodes': self.episodes,
            'status': self.status,
            'rating': self.rating,
            'image': self.image,
            'url': self.url,
            'synopsis': self.synopsis,
            'background': self.background,
            'season': self.season,
            'year': self.year,
            'genres': self.genres.split(', ') if self.genres else []
        }
    

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.now)
    avatar_hash = db.Column(db.String(32))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)



    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id})
    
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'change_email': self.id, 'new_email': new_email})
    
    def ping(self):
        self.last_seen = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
    
    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)
    
    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True
    
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
    
login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class FavoriteAnimes(db.Model):
    __tablename__ = 'favorite_animes'
    id = db.Column(db.Integer, primary_key=True)
    id_anime = db.Column(db.Integer, db.ForeignKey('animes.id'), nullable=False)  # Referencia o modelo Anime
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    anime = db.relationship('Anime', backref='favorites', lazy='select')  
    user = db.relationship('User', backref='favorites', lazy='select')  

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))