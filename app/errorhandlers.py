# -*- coding:utf-8 -*-
from flask import jsonify, render_template


def init_app(app):
    @app.errorhandler(400)
    def bad_request(e):
        response = jsonify({'message': e.description})
        response.status_code = 400
        return response

    @app.errorhandler(401)
    def unauthorized(e):
        response = jsonify({'message': 'invalid authority'})
        response.status_code = 401
        return response

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(405)
    def method_not_supported(e):
        response = jsonify({'message': 'the method is not supported'})
        response.status_code = 405
        return response

    @app.errorhandler(500)
    def internal_server_error(e):
        response = jsonify({'message': e.description})
        response.status_code = 500
        return response
