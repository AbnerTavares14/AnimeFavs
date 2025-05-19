from flask import url_for, redirect, render_template, request, jsonify, flash
from flask_login import login_required, current_user
import requests
from . import main
from .forms import AnimeForm
from ..models import Anime, FavoriteAnimes, User
from .. import db


@main.route('/', methods=['GET', 'POST'])
def index():
    form = AnimeForm()
    if form.validate_on_submit():
        title = form.title.data
        return redirect(url_for('main.search_anime', query=title))
    return render_template('home.html', form=form)


@main.route('/anime', methods=['GET'])
def search_anime():
    query = request.args.get('q', '').strip()
    user = None
    favorites = []
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        favorites = user.favorites
    if not query:
        return jsonify({'error': 'Parâmetro de busca não fornecido'}), 400

    animes = Anime.query.filter(Anime.title.ilike(f'%{query}%')).all()

    if animes:
        animes_info = [anime.to_dict() for anime in animes]
        favorites = [favorite.anime.mal_id for favorite in favorites]
        if current_user.is_authenticated:
            for anime in animes_info:
                if anime['mal_id'] in favorites: 
                    anime['favorite'] = True
                else:
                    anime['favorite'] = False
        return jsonify(animes_info)

    url = f'https://api.jikan.moe/v4/anime?q={query}'
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Anime não encontrado'}), 404

    anime_data = response.json()
    animes_info = []
    for anime in anime_data.get('data', []):
        genres_list = [genre['name'] for genre in anime.get('genres', [])]
        genres_str = ', '.join(genres_list)
        if anime in favorites: 
            anime['favorite'] = True
        else:
            anime['favorite'] = False

        anime_info = {
            'mal_id': anime.get('mal_id'),
            'title': anime.get('title'),
            'source': anime.get('source', 'N/A'),
            'episodes': anime.get('episodes', 'N/A'),
            'status': anime.get('status', 'N/A'),
            'rating': anime.get('rating', 'N/A'),
            'image': anime.get('images', {}).get('jpg', {}).get('image_url', 'N/A'),
            'url': anime.get('url'), 
            'synopsis': anime.get('synopsis'),
            'background': anime.get('background'),
            'season': anime.get('season'),
            'year': anime.get('year'),
            'genres': genres_list,
            'favorite': anime.get('favorite', False)
        }
        animes_info.append(anime_info)

        existing_anime = Anime.query.filter_by(title=anime_info['title']).first()
        if not existing_anime:
            new_anime = Anime(
                mal_id=anime_info['mal_id'],
                title=anime_info['title'],
                source=anime_info['source'],
                episodes=anime_info['episodes'] if isinstance(anime_info['episodes'], int) else None,
                status=anime_info['status'],
                rating=anime_info['rating'],
                image=anime_info['image'],
                url=anime_info['url'],
                synopsis=anime_info['synopsis'],
                background=anime_info['background'],
                season=anime_info['season'],
                year=anime_info['year'],
                genres=genres_str
            )
            db.session.add(new_anime)
    try:
        db.session.commit()
        return jsonify(animes_info)
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao salvar dados no banco'}), 500


@main.route('/favorite/<int:id>', methods=['POST'])
@login_required
def favorite_anime(id):
    user = User.query.filter_by(id=current_user.id).first()  
    anime = Anime.query.filter_by(mal_id=id).first()  

    if not anime:
        flash('Not found anime', "Error")
        return jsonify({"error": "Anime não encontrado"}), 404

    existing_favorite = FavoriteAnimes.query.filter_by(id_anime=anime.id, id_user=user.id).first()
    if existing_favorite:
        flash('Anime já está nos seus favoritos.', "Info")
        return jsonify({"message": "Anime já está nos seus favoritos."}), 200

    new_favorite_anime = FavoriteAnimes(
        id_anime=anime.id,
        id_user=user.id
    )
    
    db.session.add(new_favorite_anime)
    db.session.commit()  

    flash("Anime added to favorites!", "success")
    return jsonify({"message": "Anime added to favorites!"}), 200

@main.route('/favorites', methods=['GET'])
@login_required
def get_favorite_animes():
    user = User.query.get(current_user.id)
    favorite_animes = user.favorites
    favorite_anime_objects = [
        {
            'id': favorite.anime.mal_id,
            'title': favorite.anime.title,
            'source': favorite.anime.source,
            'episodes': favorite.anime.episodes,
            'status': favorite.anime.status,
            'rating': favorite.anime.rating,
            'image': favorite.anime.image,
            'url': favorite.anime.url,
            'synopsis': favorite.anime.synopsis,
            'background': favorite.anime.background,
            'season': favorite.anime.season,
            'year': favorite.anime.year,
            'genres': favorite.anime.genres,
        }
        for favorite in favorite_animes
    ]
    return render_template('favorites.html', favorite_animes=favorite_anime_objects)

@main.route('/remove_favorite/<int:id>', methods=['DELETE'])
@login_required
def remove_favorite_anime(id):
    print(id)
    user = User.query.filter_by(id=current_user.id).first()  
    anime = Anime.query.filter_by(mal_id=id).first()  

    if not anime:
        flash('Not found anime', "Error")
        return jsonify({"error": "Anime não encontrado"}), 404

    favorite_anime = FavoriteAnimes.query.filter_by(id_anime=anime.id, id_user=user.id).first()
    if not favorite_anime:
        flash('Anime is not in your favorites.', "Info")
        return jsonify({"message": "Anime não está nos seus favoritos."}), 200

    db.session.delete(favorite_anime)
    db.session.commit()  

    flash("Anime removed from favorites!", "success")
    return jsonify({"message": "Anime removed from favorites!"}), 200