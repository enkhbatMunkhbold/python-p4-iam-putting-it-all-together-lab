#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')        
        bio = data.get('bio')

        if not username or not password:
            return {'error': 'User must have username and password.'}, 422

        new_user = User(
            username = username,
            image_url = image_url,
            bio = bio
        )
        new_user.password_hash = password         

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
        username = data.get('username')
        password = data.get('password')
            
        user = User.query.filter(User.username == username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {}, 401
    
class Logout(Resource):
    def delete(self):
        if not session['user_id']: 
            return {}, 401
        session['user_id'] = None
        return {}, 204

class RecipeIndex(Resource):
    def get(self):

        if session['user_id']:
            user = User.query.filter(User.id == session['user_id']).first()
            return [recipe.to_dict() for recipe in user.recipes], 200
        return {}, 401

    def post(self):

        if session['user_id']:
            data = request.get_json()

            title = data.get('title')
            instructions = data.get('instructions')
            minutes_to_complete = data.get('minutes_to_complete')
            user_id = session['user_id']
            
            if not title or len(instructions) < 50:
                return {'error': 'Unprocessable Entity.'}, 422

            new_recipe = Recipe (
                title = title,
                instructions = instructions,
                minutes_to_complete = minutes_to_complete,
                user_id = user_id,
            )

            db.session.add(new_recipe)
            db.session.commit()      

            return new_recipe.to_dict(), 201
        return {'error': 'User is nauthorized'}, 401

        


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)