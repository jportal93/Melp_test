import math
import os

from dotenv import load_dotenv
from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

app = Flask(__name__)

load_dotenv()

if 'DATABASE_URL' in os.environ:
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URLL']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@db:5432/test'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app, version='1.0', title='Melp',
          description='Restaurant Info', default='CRUD')


class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.String(36), primary_key=True)
    rating = db.Column(db.Integer)
    name = db.Column(db.String(80))
    site = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    street = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


restaurant_fields = api.model('Restaurant', {
    'id': fields.String,
    'rating': fields.Integer,
    'name': fields.String,
    'site': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'street': fields.String,
    'city': fields.String,
    'state': fields.String,
    'lat': fields.Float,
    'lng': fields.Float
})


class Restaurants(Resource):
    @api.marshal_with(restaurant_fields)
    def get(self):
        restaurants = Restaurant.query.all()
        return restaurants

    @api.expect(restaurant_fields)
    @api.marshal_with(restaurant_fields)
    def post(self):
        restaurant = Restaurant(**api.payload)
        db.session.add(restaurant)
        db.session.commit()
        return restaurant


class RestaurantDetail(Resource):
    @api.marshal_with(restaurant_fields)
    def get(self, id):
        restaurant = Restaurant.query.get_or_404(id)
        return restaurant, 200

    @api.expect(restaurant_fields)
    @api.marshal_with(restaurant_fields)
    def put(self, id):
        restaurant = Restaurant.query.get_or_404(id)
        restaurant.rating = api.payload.get('rating', restaurant.rating)
        restaurant.name = api.payload.get('name', restaurant.name)
        restaurant.site = api.payload.get('site', restaurant.site)
        restaurant.email = api.payload.get('email', restaurant.email)
        restaurant.phone = api.payload.get('phone', restaurant.phone)
        restaurant.street = api.payload.get('street', restaurant.street)
        restaurant.city = api.payload.get('city', restaurant.city)
        restaurant.state = api.payload.get('state', restaurant.state)
        restaurant.lat = api.payload.get('lat', restaurant.lat)
        restaurant.lng = api.payload.get('lng', restaurant.lng)
        db.session.commit()
        return restaurant

    def delete(self, id):
        restaurant = Restaurant.query.get_or_404(id)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204


location_model = api.model('Location', {
    'latitude': fields.Float(required=True),
    'longitude': fields.Float(required=True),
    'radius': fields.Float(required=True),
})

stats_model = api.model('RestaurantStats', {
    'count': fields.Integer(required=True),
    'avg': fields.Float(required=True),
    'std': fields.Float(required=True),
})

statistics_ns = Namespace('restaurants', description='Restaurant statistics')


@statistics_ns.route('/statistics')
class RestaurantStats(Resource):
    @api.expect(location_model)
    @api.marshal_with(stats_model)
    def get(self):
        # Obtener parámetros de la petición
        latitude = api.payload['latitude']
        longitude = api.payload['longitude']
        radius = api.payload['radius']
        radius_degrees = radius / 111000

        restaurants = Restaurant.query.filter(and_(
            Restaurant.lat.between(latitude - radius_degrees, latitude + radius_degrees),
            Restaurant.lng.between(longitude - radius_degrees, longitude + radius_degrees)
        )).all()

        count = len(restaurants)
        avg = sum(restaurant.rating for restaurant in restaurants) / count if count > 0 else 0
        std = math.sqrt(sum((restaurant.rating - avg) ** 2 for restaurant in restaurants) / count) if count > 0 else 0

        # Devolver la respuesta como un objeto JSON
        return {'count': count, 'avg': avg, 'std': std}, 200


api.add_namespace(statistics_ns)

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantDetail, '/restaurants/<string:id>')

if __name__ == '__main__':
    app.run('0.0.0.0')
