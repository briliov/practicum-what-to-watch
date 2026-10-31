from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import Opinion
from .views import random_opinion


@app.route('/api/opinions/<int:id>/', methods=['GET'])
def get_opinion(id: int):
    opinion: Opinion = Opinion.query.get_or_404(id)
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['PATCH'])
def update_opinion(id: int):
    data = request.get_json()
    if (
        'text' in data
        and Opinion.query.filter_by(text=data['text']).first() is not None
    ):
        return jsonify({'error': 'Такое мнение уже есть в базе данных'}), 400
    opinion: Opinion = Opinion.query.get_or_404(id)
    opinion.title = request.json.get('title', opinion.title)
    opinion.text = request.json.get('text', opinion.text)
    opinion.source = request.json.get('source', opinion.source)
    opinion.added_by = request.json.get('added_by', opinion.added_by)
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['DELETE'])
def delete_opinion(id: int):
    opinion: Opinion = Opinion.query.get_or_404(id)
    db.session.delete(opinion)
    db.session.commit()
    return '', 204


@app.route('/api/opinions/', methods=['GET'])
def get_opinions():
    opinions: list[Opinion] = Opinion.query.all()
    opinions_list: list = [opinion.to_dict() for opinion in opinions]
    return jsonify({'opinions': opinions_list}), 200


@app.route('/api/opinions/', methods=['POST'])
def add_opinion():
    data = request.get_json()
    if 'title' not in data or 'text' not in data:
        raise InvalidAPIUsage('В запросе отсутствуют обязательные поля')
    if Opinion.query.filter_by(text=data['text']).first is not None:
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    opinion: Opinion = Opinion()
    opinion.from_dict(data)
    db.session.add(opinion)
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 201


@app.route('/api/get-random-opinion/', methods=['GET'])
def get_random_opinion():
    opinion: Opinion | None = random_opinion()
    if opinion is not None:
        return jsonify({'opinion': opinion.to_dict()}), 200
    raise InvalidAPIUsage('В базе данных нет мнений', 404)
