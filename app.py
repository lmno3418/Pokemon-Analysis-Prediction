from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
import json
import os
import ast
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')

# Initialize MongoDB client
mongo_uri = os.environ.get("mongo_uri", "mongodb://localhost:27017/pokedex")
client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
db = client["pokedex_db"]
users_collection = db["users"]

# Create index on email for faster lookups
users_collection.create_index("email", unique=True)

# Create index on username for faster lookups and uniqueness
users_collection.create_index("username", unique=True)

# Setup login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Type mappings for the battle model
TYPE_MAPPING = {
    'Bug': 0, 'Dark': 1, 'Dragon': 2, 'Electric': 3, 'Fairy': 4,
    'Fighting': 5, 'Fire': 6, 'Flying': 7, 'Ghost': 8, 'Grass': 9,
    'Ground': 10, 'Ice': 11, 'Normal': 12, 'Poison': 13, 'Psychic': 14,
    'Rock': 15, 'Steel': 16, 'Water': 17
}

# User model
class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = str(id)
        self.username = username
        self.email = email
        self.password = password
        
    @staticmethod
    def get_by_id(user_id):
        try:
            user_data = users_collection.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User(
                    id=user_data['_id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password']
                )
        except Exception as e:
            print(f"Error getting user by id: {e}")
        return None
    
    @staticmethod
    def get_by_email(email):
        try:
            user_data = users_collection.find_one({"email": email})
            if user_data:
                return User(
                    id=user_data['_id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password']
                )
        except Exception as e:
            print(f"Error getting user by email: {e}")
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Load Pokemon data
def load_pokemon_data():
    data_path = os.path.join(os.path.dirname(__file__), "static/data/PokemonData2.json")
    try:
        with open(data_path, "r") as f:
            raw_pokemon_data = json.load(f)

        # Transform data to match expected format
        transformed_data = []
        for pokemon in raw_pokemon_data:
            # Parse sprite data
            sprite_data = {}
            try:
                if isinstance(pokemon["sprites"], str):
                    sprite_data = ast.literal_eval(pokemon["sprites"])
                else:
                    sprite_data = pokemon["sprites"]
            except Exception as e:
                print(f"Error parsing sprites for {pokemon['Name']}: {str(e)}")
                sprite_data = {"normal": "", "animated": ""}

            transformed_pokemon = {
                "id": pokemon["#"],
                "name": pokemon["Name"],
                "type1": pokemon["Type 1"],
                "type2": pokemon["Type 2"] if pokemon["Type 2"] != "Normal" else "",
                "hp": pokemon["HP"],
                "attack": pokemon["Attack"],
                "defense": pokemon["Defense"],
                "sp_atk": pokemon["Sp. Atk"],
                "sp_def": pokemon["Sp. Def"],
                "speed": pokemon["Speed"],
                "generation": pokemon["Generation"],
                "legendary": pokemon["Legendary"],
                "height": pokemon["height"],
                "weight": pokemon["weight"],
                "base_experience": pokemon["base_experience"],
                "sprites": sprite_data,
            }
            transformed_data.append(transformed_pokemon)
        
        print(f"Successfully loaded {len(transformed_data)} Pokémon")
        return transformed_data
    except Exception as e:
        print(f"ERROR loading Pokémon data: {str(e)}")
        return []

# Load battle prediction model
def load_battle_model():
    model_path = os.path.join(os.path.dirname(__file__), "static/data/pokemon_RandomForest_model.pkl")
    try:
        model = joblib.load(model_path)
        print("Battle model loaded successfully!")
        return model
    except Exception as e:
        print(f"Error loading battle model: {e}")
        return None

# Convert Pokémon data to features for battle prediction
def pokemon_to_features(pokemon):
    total_stats = (
        pokemon["hp"] + pokemon["attack"] + pokemon["defense"] + 
        pokemon["sp_atk"] + pokemon["sp_def"] + pokemon["speed"]
    )
    
    return {
        'type1': pokemon["type1"],
        'type2': pokemon["type2"] if pokemon["type2"] != "" else None,
        'height': pokemon["height"] / 10,  # Convert to meters
        'weight': pokemon["weight"] / 10,  # Convert to kg
        'base_experience': pokemon["base_experience"],
        'generation': pokemon["generation"],
        'legendary': pokemon["legendary"],
        'total_stats': total_stats
    }

# Predict battle outcome between two Pokemon
def predict_battle(model, pokemon1_features, pokemon2_features):
    if model is None:
        return {"error": "Battle model is not available"}
    
    # Extract pokemon features
    type1_first = TYPE_MAPPING.get(pokemon1_features['type1'], None)
    type2_first = TYPE_MAPPING.get(pokemon1_features.get('type2', None), None)
    type1_second = TYPE_MAPPING.get(pokemon2_features['type1'], None)
    type2_second = TYPE_MAPPING.get(pokemon2_features.get('type2', None), None)
    
    # Calculate differences (pokemon1 - pokemon2)
    height_diff = pokemon1_features['height'] - pokemon2_features['height']
    weight_diff = pokemon1_features['weight'] - pokemon2_features['weight']
    exp_diff = pokemon1_features['base_experience'] - pokemon2_features['base_experience']
    total_stats_diff = pokemon1_features['total_stats'] - pokemon2_features['total_stats']
    gen_diff = pokemon1_features['generation'] - pokemon2_features['generation']
    legendary_diff = int(pokemon1_features['legendary']) - int(pokemon2_features['legendary'])
    
    # Create a feature array for prediction
    features = np.array([
        type1_first, type2_first, type1_second, type2_second,
        height_diff, weight_diff, exp_diff, total_stats_diff,
        gen_diff, legendary_diff
    ]).reshape(1, -1)
    
    # Make prediction
    try:
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
        
        return {
            'winner': 'Pokemon 1' if prediction == 1 else 'Pokemon 2',
            'probability': max(probability) * 100
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        return {"error": f"Error making prediction: {str(e)}"}

# Initialize data
pokemon_data = load_pokemon_data()
battle_model = load_battle_model()

# Initialize Dash dashboard
from dashboard import create_dashboard, load_pokemon_dataframe

pokemon_df = load_pokemon_dataframe()
dashboard_app = create_dashboard(app, pokemon_df)

# Protect dashboard with login_required
@app.before_request
def check_dashboard_auth():
    if request.path.startswith('/dashboard/'):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))

# Authentication routes
@app.route('/')
def home():
    return render_template('home.html', title='Home')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('pokedex'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        
        # Check if email already exists
        existing_email = users_collection.find_one({"email": form.email.data})
        if existing_email:
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('register.html', title='Register', form=form)
        
        # Check if username already exists
        existing_username = users_collection.find_one({"username": form.username.data})
        if existing_username:
            flash('Username already taken. Please choose a different username.', 'danger')
            return render_template('register.html', title='Register', form=form)
        
        # Create new user
        new_user = {
            'username': form.username.data,
            'email': form.email.data,
            'password': hashed_password
        }
        
        try:
            result = users_collection.insert_one(new_user)
            if result.inserted_id:
                flash('Your account has been created! You are now able to log in', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please try again.', 'danger')
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('pokedex'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username_or_email = form.username_or_email.data
        
        # Try to find by email first, then by username
        user_data = users_collection.find_one({"email": username_or_email})
        if not user_data:
            user_data = users_collection.find_one({"username": username_or_email})
        
        if user_data and check_password_hash(user_data['password'], form.password.data):
            user = User(
                id=user_data['_id'],
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('pokedex'))
        else:
            flash('Login Unsuccessful. Please check username/email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Pokedex routes (protected by authentication)
@app.route('/pokedex')
@login_required
def pokedex():
    return render_template('pokedex.html', title="Pokedex")

@app.route("/api/pokemon")
@login_required
def get_pokemon():
    search_query = request.args.get("search", "").lower()

    # Standard filters
    filters = {
        "height": request.args.get("height"),
        "weight": request.args.get("weight"),
        "base_experience": request.args.get("base_experience"),
        "type1": request.args.get("type1"),
        "type2": request.args.get("type2"),
        "generation": request.args.get("generation"),
        "legendary": request.args.get("legendary"),
    }

    # Range filters
    range_filters = {
        "hp": {"min": request.args.get("hp_min"), "max": request.args.get("hp_max")},
        "attack": {"min": request.args.get("attack_min"), "max": request.args.get("attack_max")},
        "defense": {"min": request.args.get("defense_min"), "max": request.args.get("defense_max")},
        "sp_atk": {"min": request.args.get("sp_atk_min"), "max": request.args.get("sp_atk_max")},
        "sp_def": {"min": request.args.get("sp_def_min"), "max": request.args.get("sp_def_max")},
        "speed": {"min": request.args.get("speed_min"), "max": request.args.get("speed_max")},
    }

    def matches_filters(pokemon):
        # Check standard filters
        for key, value in filters.items():
            if value is not None and value != "":
                if key == "legendary":
                    pokemon_value = pokemon.get(key, False)
                    filter_value = value.lower() == "true"
                    if pokemon_value != filter_value:
                        return False
                elif key == "type2" and value.lower() == "none":
                    if pokemon.get(key, None) is not None and pokemon.get(key, "") != "":
                        return False
                elif str(pokemon.get(key, "")).lower() != value.lower():
                    return False

        # Check range filters
        for stat, range_values in range_filters.items():
            min_val = range_values["min"]
            max_val = range_values["max"]

            if min_val is not None and min_val != "":
                try:
                    if int(pokemon.get(stat, 0)) < int(min_val):
                        return False
                except ValueError:
                    pass

            if max_val is not None and max_val != "":
                try:
                    if int(pokemon.get(stat, 0)) > int(max_val):
                        return False
                except ValueError:
                    pass

        return True

    # Apply search query and filters
    if search_query:
        filtered_pokemon = [
            pokemon
            for pokemon in pokemon_data
            if search_query in pokemon.get("name", "").lower()
            and matches_filters(pokemon)
        ]
    else:
        filtered_pokemon = [
            pokemon for pokemon in pokemon_data if matches_filters(pokemon)
        ]

    return jsonify(filtered_pokemon)

@app.route("/api/pokemon/<pokemon_id>")
@login_required
def get_pokemon_by_id(pokemon_id):
    for pokemon in pokemon_data:
        if str(pokemon.get("id")) == str(pokemon_id):
            return jsonify(pokemon)

    return jsonify({"error": "Pokemon not found"}), 404

# API endpoint for battle predictions
@app.route('/api/battle', methods=['POST'])
@login_required
def api_battle():
    # Get JSON data from request
    data = request.json
    
    if not data or 'pokemon1' not in data or 'pokemon2' not in data:
        return jsonify({'error': 'Missing required Pokemon data'}), 400
    
    # Get selected Pokemon names
    pokemon1_name = data['pokemon1']
    pokemon2_name = data['pokemon2']
    
    # Find Pokemon data
    pokemon1 = next((p for p in pokemon_data if p["name"].lower() == pokemon1_name.lower()), None)
    pokemon2 = next((p for p in pokemon_data if p["name"].lower() == pokemon2_name.lower()), None)
    
    if not pokemon1 or not pokemon2:
        return jsonify({'error': 'One or both Pokémon not found'}), 404
    
    # Convert Pokemon data to features
    pokemon1_features = pokemon_to_features(pokemon1)
    pokemon2_features = pokemon_to_features(pokemon2)
    
    # Predict battle outcome
    result = predict_battle(battle_model, pokemon1_features, pokemon2_features)
    
    if "error" in result:
        return jsonify({'error': result["error"]}), 500
    
    # Format battle result for response
    winner_name = pokemon1["name"] if result["winner"] == "Pokemon 1" else pokemon2["name"]
    battle_result = {
        "winner": winner_name,
        "probability": float(round(result["probability"], 2))
    }
    
    return jsonify(battle_result)

if __name__ == "__main__":
    # For HF Spaces: use port 7860, for local: use port 5000
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
 
