import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from .auth.auth import get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


@app.route('/test')
def test():
    return "Server Up !, keep Coding "


@app.route('/login-results', methods=['Get', 'Post'])
def login_result():
    return str(get_token_auth_header())


# ROUTES
'''
@TO-done-DO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drink():
    drinks = Drink.query.all()
    drink_array = []
    for drink in drinks:
        drink_array.append(drink.short())
    return jsonify({"success": True, "drinks": drink_array})


'''
@TO-done-DO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth(permissions=['get:drinks-detail'])
def get_drink_detail(paload):
    drinks = Drink.query.all()
    drink_array = []
    for drink in drinks:
        drink_array.append(drink.long())
    return jsonify({"success": True, "drinks": drink_array})


'''
@TO-done-DO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
        recipe --> [{'color': string, 'name':string, 'parts':number}]
     json data=   {
    "title":"drink_1 title",
    "recipe":{"color": "red", "name":"drink_1_ingre_1", "parts":2}
}
'''


@app.route('/drinks', methods=['POST'])
@requires_auth(permissions=['post:drinks'])
def post_drink(paload):
    try:
        title = request.get_json()['title']
        recipe = request.get_json()['recipe']
        if len(Drink.query.filter(Drink.title == str(title)).all()) > 0:
            abort(422)
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({"success": True, "drinks": [drink.long()]})
    except Exception:
        abort(422)


'''
@TO-done-DO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth(permissions=['patch:drinks'])
def patch_drink(paload, id):
    try:
        drink = Drink.query.filter(Drink.id == int(id)).first()
        if not drink:
            abort(404)
        if ('title' not in request.get_json()) and ('recipe' not in request.get_json()):
            abort(422)
        if 'title' in request.get_json():
            drink.title = request.get_json()['title']
        if 'recipe' in request.get_json():
            drink.recipe = str(request.get_json()['recipe']).replace("'", '"')
        Drink.update(drink)
        return jsonify({"success": True, "drinks": [drink.long()]})

    except Exception:
        abort(422)


'''
@TO-done-DO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth(permissions=['delete:drinks'])
def delete_drink(paload, id):
    try:
        drink = Drink.query.filter(Drink.id == int(id)).first()
        if not drink:
            abort(404)
        Drink.delete(drink)
        return jsonify({"success": True, "delete": id})
    except Exception:
        abort(422)


# Error Handling
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


'''
@TO-done-DO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TO-done-DO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "un authorized"
    }), 401


'''
@TO-done-DO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def auth_error(auth):
    return jsonify({
        "success": False,
        "error": auth.status_code,
        "message": auth.error
    }), auth.status_code
