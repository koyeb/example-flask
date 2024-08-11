from flask import Flask, render_template
from flask_restplus import Api, Resource
app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello from Koyeb'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')


api = Api(app, version='1.0', title='My Octopus API', description='A simple API to retrieve my Octopus tariff data')

ns = api.namespace('my_tariff_namespace', description='Tariff Namespace operations')

@ns.route('/tariff')
class HelloWorld(Resource):
    def get(self):
        '''Returns a greeting'''
        return {'hello': 'world'}


if __name__ == "__main__":
    app.run(debug=True)
