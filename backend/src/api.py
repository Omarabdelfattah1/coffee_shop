import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#db_drop_and_create_all()

## ROUTES
# Get all drinks enddpoint
@app.route('/drinks')
def drinks():
    drinks=Drink.query.all()
    short_representation=[]
    for drink in drinks:
        short_representation.append(drink.short())
    return jsonify({
        "success":True,
        "drinks":short_representation
    })

# Show a drink details 
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
    drinks = Drink.query.all()
    long_representation=[]
    for drink in drinks:
        long_representation.append(drink.long())
    return jsonify({
        'success': True,
        'drinks': long_representation
    }), 200


# Post new drink endpoint

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    req = request.get_json()

    try:
        if isinstance(req['recipe'], dict):
            req['recipe'] = [req['recipe']]
        drink = Drink(title=req['title'] ,recipe=json.dumps(req['recipe']))
        drink.insert()

    except BaseException:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]})

# Update drink endpoint
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    req = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    try:
        if req.get('title'):
            drink.title = req.get('title')

        if req.get('recipe'):
            drink.recipe = json.dumps(req.get('recipe'))
        drink.update()
    except BaseException:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200

# Delete drink endpoint.
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    try:
        drink.delete()
    except BaseException:
        abort(400)

    return jsonify({'success': True, 'drinks': id}), 200



## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

# Error handler for "Not found"
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Not Found"
                    }), 404

# Error handler for "unauthorized"
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "You are not authorized to do this action."
                    }), 401

# Error handler for "forbidden"
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
                    "success": False, 
                    "error": 403,
                    "message": "Forbidden"
                    }), 403


