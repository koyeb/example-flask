from flask import Flask, render_template, request, jsonify
import numpy as np
import os
import json
import random

app = Flask(__name__)

# Load the pre-trained model architecture
model_json_file = 'text_generation_model.json'

if not os.path.exists(model_json_file):
    print("Model architecture file not found.")
    exit() 

with open(model_json_file, 'r') as json_file:
    model_architecture = json.load(json_file)

input_dim = model_architecture['input_dim']
output_dim = model_architecture['output_dim']
word_to_index = model_architecture['word_to_index']
index_to_word = model_architecture['index_to_word']

# Initialize random weights and biases if the weight files are not available
try:
    weights_hidden = np.loadtxt('weights_hidden.csv', delimiter=',')
    biases_hidden = np.loadtxt('biases_hidden.csv', delimiter=',')
    weights_output = np.loadtxt('weights_output.csv', delimiter=',')
    biases_output = np.loadtxt('biases_output.csv', delimiter=',')
except OSError:
    # Initialize random weights if files are not found
    weights_hidden = np.random.randn(input_dim, 128)
    biases_hidden = np.zeros(128)
    weights_output = np.random.randn(128, output_dim)
    biases_output = np.zeros(output_dim)

def generate_text(seed_text, next_words, model_architecture, temperature=1.0):
    generated_text = seed_text
    recent_words = seed_text.split()

    for _ in range(next_words):
        # Check if the most recent word is in the vocabulary
        if recent_words[-1] in model_architecture['word_to_index']:
            # Placeholder logic: Sample the next word randomly
            next_word_index = np.random.choice(range(model_architecture['output_dim']))
            next_word = model_architecture['index_to_word'][str(next_word_index)]

            # Check if the next word is the same as the seed word
            if next_word.lower() == seed_text.lower():
                return "Sorry, I don't know.😓"

            # Append the sampled word to the generated text
            generated_text += " " + next_word
            recent_words.append(next_word)

            if len(recent_words) > model_architecture['input_dim'] - 1:
                recent_words.pop(0)
        else:
            break

    return generated_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_input = request.form['query']
    response = generate_text(user_input, next_words=50, model_architecture=model_architecture, temperature=1.7)
    return jsonify({'success': True, 'message': response})

if __name__ == '__main__':
    app.run(debug=True)
