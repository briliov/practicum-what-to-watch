from flask import jsonify, request

from . import app, db
from .models import Opinion


@app.route('/api/opinions/<int:id>/', methods=['GET'])
def get_opinion(id: int):
    opinion: Opinion = Opinion.query.get_or_404(id)
    return jsonify({'opinion': opinion.to_dict()}), 200


