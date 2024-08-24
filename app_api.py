from flask import Flask
from flask_restful import Api, Resource
from flasgger import Swagger

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

class Hello(Resource):
    def get(self):
        """
        A hello world endpoint
        ---
        responses:
          200:
            description: Returns a greeting
            examples:
              application/json: {"hello": "world"}
        """
        return {'hello': 'world'}

api.add_resource(Hello, '/hello')

if __name__ == '__main__':
    app.run(debug=True)
