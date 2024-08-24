from flask import Flask
from flask_restplus import Api, Resource

app = Flask(__name__)
api = Api(app, version='1.0', title='My API', description='A simple API')

ns = api.namespace('my_namespace', description='Namespace operations')

@ns.route('/hello')
class HelloWorld(Resource):
    def get(self):
        '''Returns a greeting'''
        return {'hello': 'world'}

if __name__ == '__main__':
    app.run(debug=True)
