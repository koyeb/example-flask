from flask import Flask, render_template, request, redirect, url_for, session
from user_authentication import register_user, login_user, create_table
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
create_table()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone_number = request.form['phone_number']
        
        # Register user and redirect to login page
        register_user(username, password, email, phone_number)
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if login credentials are valid
        user = login_user(username, password)
        if user:
            # Set session for logged-in user
            session['username'] = user[0]  # Storing username in session
            if username == 'trainer':  # Check if the username is 'trainer'
                return redirect(url_for('trainer_dashboard'))  # Redirect to trainer dashboard
            else:
                return redirect(url_for('dashboard'))  # Redirect to user's dashboard
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')
    
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    # Check if user is logged in (session exists)
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))
    
    
@app.route('/trainer_dashboard', methods=['GET', 'POST'])
def trainer_dashboard():
    exercises = [
        "Push-up", "Squats", "Pull-ups", "Plank", "Lunges", "Sit-ups", "Calf Raises",
        "Bench Press", "Bicep Curls", "Tricep Extensions", "Shoulder Press", "Deadlift",
        # Add more exercises here...
    ]
    if request.method == 'POST':
    # Retrieve existing workout details or initialize an empty list
        workout_details = session.get('workout_details', [])

    # Extract exercise details from the form
        exercise = request.form.get('exercise')
        sets = request.form.get('sets')
        reps = request.form.get('reps')
        rest = request.form.get('rest')
        message = request.form.get('message')

    # Append new exercise details to the existing list
        workout_details.append({
            'exercise': exercise,
            'sets': sets,
            'reps': reps,
            'rest': rest,
            'message': message
         })

    # Store the updated workout details in the session
        session['workout_details'] = workout_details

    return render_template('trainer_dashboard.html', workout_details=session.get('workout_details'), exercises=exercises)

@app.route('/logout')
def logout():
    # Clear session data to log out the user
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/exercise_library')
def exercise_library():
    return render_template('exercise_library.html')

@app.route('/workouts', methods=['GET', 'POST'])
def workouts():
    if request.method == 'POST' and request.form.get('clear_workouts'):
        session.pop('workout_details', None)
        return redirect(url_for('workouts'))
    workout_details = session.get('workout_details')
    return render_template('workouts.html', workout_details=workout_details)

recipes = [
    {
        "name": "Avocado Toast",
        "ingredients": ["Avocado", "Bread", "Salt", "Pepper"],
        "nutrition": {
            "calories": 200,
            "carbs": 15,
            "protein": 5,
            "fat": 15
        }
    },
    {
        "name": "Chicken Salad",
        "ingredients": ["Chicken", "Lettuce", "Tomato", "Cucumber", "Dressing"],
        "nutrition": {
            "calories": 300,
            "carbs": 10,
            "protein": 25,
            "fat": 18
        }
    },
    {
        'name': 'Protein Shake',
        'ingredients': ['Protein Powder', 'Milk', 'Banana'],
        'nutrition': {
            'calories': 300,
            'carbs': 45,
            'protein': 30,
            'fat': 5
        }
    },
    {
        'name': 'Pasta',
        'ingredients': ['Pasta', 'Tomato Sauce', 'Ground Beef'],
        'nutrition': {
            'calories': 500,
            'carbs': 60,
            'protein': 25,
            'fat': 15
        }
    },
    {
        'name': 'Oatmeal',
        'ingredients': ['Oats', 'Milk', 'Honey'],
        'nutrition': {
            'calories': 250,
            'carbs': 45,
            'protein': 10,
            'fat': 5
        }
    },
    {
        'name': 'Steak and Potatoes',
        'ingredients': ['Steak', 'Potatoes', 'Butter'],
        'nutrition': {
            'calories': 700,
            'carbs': 30,
            'protein': 50,
            'fat': 40
        }
    },
    {
        'name': 'Salmon',
        'ingredients': ['Salmon', 'Lemon', 'Salt', 'Pepper'],
        'nutrition': {
            'calories': 400,
            'carbs': 0,
            'protein': 40,
            'fat': 25
        }
    },
    {
        'name': 'Eggs and Toast',
        'ingredients': ['Eggs', 'Bread', 'Butter'],
        'nutrition': {
            'calories': 300,
            'carbs': 30,
            'protein': 15,
            'fat': 15
        }
    },
    {
        'name': 'Tuna Sandwich',
        'ingredients': ['Tuna', 'Bread', 'Mayo'],
        'nutrition': {
            'calories': 400,
            'carbs': 30,
            'protein': 20,
            'fat': 20
        }
    },
    {
        'name': 'Chicken and Rice',
        'ingredients': ['Chicken', 'Rice', 'Soy Sauce'],
        'nutrition': {
            'calories': 500,
            'carbs': 45,
            'protein': 40,
            'fat': 10
        }
    },
    {
        'name': 'Peanut Butter and Jelly Sandwich',
        'ingredients': ['Bread', 'Peanut Butter', 'Jelly'],
        'nutrition': {
            'calories': 400,
            'carbs': 45,
            'protein': 10,
            'fat': 20
        }
    },
    {
        'name': 'Fruit Salad',
        'ingredients': ['Apple', 'Banana', 'Orange', 'Grapes'],
        'nutrition': {
            'calories': 200,
            'carbs': 45,
            'protein': 5,
            'fat': 0
        }
    },
    {
        'name': 'Chicken Noodle Soup',
        'ingredients': ['Chicken', 'Noodles', 'Carrots', 'Celery', 'Chicken Broth'],
        'nutrition': {
            'calories': 300,
            'carbs': 30,
            'protein': 20,
            'fat': 10
        }
    },
    {
        'name': 'Chicken Tacos',
        'ingredients': ['Chicken', 'Tortilla', 'Lettuce', 'Tomato', 'Sour Cream'],
        'nutrition': {
            'calories': 400,
            'carbs': 30,
            'protein': 25,
            'fat': 20
        }
    },
    {
        'name': 'Pancakes',
        'ingredients': ['Pancake Mix', 'Milk', 'Eggs', 'Butter'],
        'nutrition': {
            'calories': 500,
            'carbs': 60,
            'protein': 10,
            'fat': 20
        }
    },
    {
        'name': 'Waffles',
        'ingredients': ['Waffle Mix', 'Milk', 'Eggs', 'Butter'],
        'nutrition': {
            'calories': 500,
            'carbs': 60,
            'protein': 10,
            'fat': 20
        }
    },
    {
        'name': 'French Toast',
        'ingredients': ['Bread', 'Milk', 'Eggs', 'Butter'],
        'nutrition': {
            'calories': 500,
            'carbs': 60,
            'protein': 10,
            'fat': 20
        }
    },
    {
        'name': 'Chicken Wings',
        'ingredients': ['Chicken Wings', 'Buffalo Sauce', 'Ranch'],
        'nutrition': {
            'calories': 600,
            'carbs': 0,
            'protein': 40,
            'fat': 40
        }
    }
]
@app.route('/nutrition', methods=['GET', 'POST'])
def nutrition():
    return render_template('nutrition.html', recipes=recipes)

@app.route('/progress')
def progress():
    dates = ['Jan 1', 'Jan 5', 'Jan 10', 'Jan 15', 'Jan 20']
    weights = [150, 149, 148, 147, 146]

    # Create the chart
    plt.figure(figsize=(10, 6))
    plt.plot(dates, weights, marker='o', linestyle='-')
    plt.title('Weight Progress')
    plt.xlabel('Date')
    plt.ylabel('Weight (lbs)')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()

    # Save the chart to a bytes object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()

    # Render the chart in an HTML template
    return render_template('progress.html', chart_url=chart_url)

@app.route('/save_progress', methods=['POST'])
def save_progress():
    weight = request.form.get('weight')
    date = request.form.get('date')
    
    if weight and date:
        # Save weight and date to database
        if 'user_progress' not in session:
            session['user_progress'] = []
        session['user_progress'].append({"weight": weight, "date": date})
    
    return redirect(url_for('progress'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
