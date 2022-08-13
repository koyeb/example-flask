from flask import Flask
from flask import request
from verify_ml import verify_ml_dataset

app = Flask(__name__)


@app.route('/verify', methods=['POST'])
def verify():
    if request.method == 'POST':
        return verify_ml_dataset(request.form['data'])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
