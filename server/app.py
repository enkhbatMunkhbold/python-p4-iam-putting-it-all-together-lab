#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        username = request.get_json()['username']
        image_url = request.get_json()['image_url']
        bio = request.get_json()['bio']

        new_user = User(
            username = username,
            image_url = image_url,
            bio = bio
        )
        new_user.password_hash = request.get_json()['password']

        if not new_user.username or not new_user.password_hash:
            return {'error': 'User must have username and password.'}, 422

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        return new_user.to_dict(), 201

class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        return {}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        user = User.query.filter(User.username == username).first()

        if user:
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {}, 401

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204

class RecipeIndex(Resource):
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)