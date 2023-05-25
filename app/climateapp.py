"""Code Rendering and Connecting HTML Pages"""
from flask import render_template, make_response, request, redirect, session
from flask import url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from api import cost_emissions, dist_emissions, flight_emissions
import hashlib
from config import app
import re
from db import db, User
from constants import *
from decimal import Decimal
FORM_DATA = 'FORM_DATA'

# Redirect http request to https requests
@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url)

#----------------------------------Search Page----------------------------------#
@app.route('/search', methods=['GET'])
def search():
    html = render_template('search.html')
    response = make_response(html)
    return response

@app.route('/updatesearch', methods=['GET'])
def updatesearch():
    field = request.args.get('user')

    # Check for empty search
    if field == "":
        return ""

    final_field = field + "%"
    found_users = User.query.filter(User.username.like(final_field)).all()

    html = ""
    for user in found_users:
        html += f"<div id='search_results_box'><a href='/results?username={user.username}' id='search_results'><i>{user.username}</i></a></div><br>"


    return html

#----------------------------------Navbar Links----------------------------------#
@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    html = render_template('index.html')
    response = make_response(html)
    return response

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    if current_user.is_anonymous:
        flash("Please register an account or login to view your profile!")
    if current_user.submission_count != 0:
        return redirect(url_for('results'))
    else:
        html = render_template('profile.html')
        response = make_response(html)
        return response

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    all_users = User.query.filter(User.submission_count != 0).all()
    all_users.sort()


    html = render_template('leaderboard.html', all_users = all_users)
    response = make_response(html)
    return response

#-----------------------------Forms-------------------------------------------

@app.route('/form', methods=['GET'])
@login_required
def form():
    session.pop(FORM_DATA, default=None)
    session[FORM_DATA] = {}
    session.modified = True
    return redirect(url_for('transport_type'))

@app.route('/transport-type', methods=['GET'])
@login_required
def transport_type():
    html = render_template('form_steps/transport-type.html')
    response = make_response(html)
    return response

TRANSPORT_TYPES = {"gascar": "gas car",
                   "evcar": "electric car", 
                   "taxi": "taxi or rideshare", 
                   "bus": "bus", 
                   "rail": "transit rail", 
                   "bike": "bike", 
                   "walking": "walking", 
                   "none": "none of the above"}

DISTANCE_TYPES = ["gascar_dist", "evcar_dist", "taxi_dist", "bus_dist", "rail_dist", "bike_dust", "walking_dist"]

@app.route('/transport-dist', methods=['POST'])
@login_required
def transport_dist():
    #Getting what transportation types the user selected
    selected_transport_types = {}
    for key, value in TRANSPORT_TYPES.items():
        if request.form.get(key) is not None:
            selected_transport_types[key] = value

    #User did not select any weekly travel -> Go straight to trips
    if len(selected_transport_types) == 0:
        return redirect(url_for('transport_trips'))
    #Go to weekly transportation distance page
    else:
        html = render_template('form_steps/transport-dist.html',
                                selected_transport_types = selected_transport_types)
        response = make_response(html)
        return response
    
DISTANCE_TYPES = ["gascar_distance", "evcar_distance", "taxi_distance", "bus_distance", "rail_distance", "bike_distance", "walking_distance"]

@app.route('/handler-dist', methods=['POST'])
@login_required
def handler_dist():
    
    #Get miles per weekly travel type and store them as values to dist_type keys in session form data
    for activity in DISTANCE_TYPES:
        if request.form.get(activity) is not None:
            if activity == 'bike_distance' or activity == 'walking_distance':
                activity_id = None
            else:
                activity_id = ID_DICT[activity]
            session[FORM_DATA][activity] = [int(request.form.get(activity)), activity_id]

    session.modified = True
    return redirect(url_for('transport_trips'))

@app.route('/transport-trips', methods=['GET'])
@login_required
def transport_trips():
    html = render_template('form_steps/transport-trips.html')
    response = make_response(html)
    return response

FLIGHT_PARTS = ["origin_airport", "destination_airport", "accomodation_length"]
TRIP_TYPES = ["flight"]


def is_valid_airport_code(code):
    if code == "":
        return True
    pattern = "^[A-Z]{3}$"
    match = re.match(pattern, code)
    return bool(match)

@app.route('/handler-trips', methods=['POST'])
@login_required
def handler_trips():
    origin_list = request.form.getlist('origin_airport')
    destination_list = request.form.getlist('destination_airport')

    for item in origin_list:
        if is_valid_airport_code(item) == False:
            flash("Invalid airport code. Please try again.")

            return redirect(url_for('transport_trips'))

    for item in destination_list:
        if is_valid_airport_code(item) == False:
            flash("Invalid airport code. Please try again.")
            return redirect(url_for('transport_trips'))
        

    # accomodation_list = request.form.get('accomodation_length')
    
    #Convert to list if single character
    if not isinstance(origin_list, list):
        origin_list = [origin_list]
        destination_list = [destination_list]
    session[FORM_DATA]['flight'] = []
    
    # Save origin-dest flight pairs to session data
    for origin, dest in zip(origin_list, destination_list):
        session[FORM_DATA]['flight'].append([origin, dest])
        
    session.modified = True
    return redirect(url_for('clothing'))

@app.route('/clothing', methods=['GET'])
@login_required
def clothing():
    html = render_template('form_steps/clothing.html')
    response = make_response(html)
    return response

CLOTHING_TYPES = ['leather', 'footwear', 'fur', 'hats', 'other']

@app.route('/handler-clothing', methods=['POST'])
@login_required
def handle_clothing():
    leather = request.form.get('leather')
    footwear = request.form.get('footwear')
    fur = request.form.get('fur')
    hats = request.form.get('hats')
    other = request.form.get('other')
        
    args = {
            'leather': (int(leather), ID_LEATHER),
            'footwear': (int(footwear),ID_FOOTWEAR),
            'fur': (int(fur), ID_FUR),
            'hats': (int(hats), ID_HATS),
            'other': (int(other), ID_OTHER)
    }
    
    for key in args.keys():
        session[FORM_DATA][key] = args[key]
    
    session.modified = True
    return redirect(url_for('food'))

@app.route('/food', methods=['GET'])
@login_required
def food():
    html = render_template('form_steps/food.html')
    response = make_response(html)
    return response

FOOD_TYPES = [
'dairy_products',
'beef_products',
'pork_products',
'poultry_products',
'seafood_products',
'fruits_vegetables',
'frozen_food',
'pet_food']

@app.route('/handler-food', methods=['POST'])
@login_required
def handle_food():
    dairy_products = request.form.get('dairy_products')
    beef_products = request.form.get('beef_products')
    pork_products = request.form.get('pork_products')
    poultry_products = request.form.get('poultry_products')
    seafood_products = request.form.get('seafood_products')
    fruits_vegetables = request.form.get('fruits_vegetables')
    frozen_food = request.form.get('frozen_food')
    pet_food = request.form.get('pet_food')
    
    args = {
            'dairy_products': (int(dairy_products), ID_DAIRY),
            'beef_products': (int(beef_products), ID_BEEF),
            'pork_products': (int(pork_products), ID_PORK),
            'poultry_products': (int(poultry_products), ID_POULTRY),
            'seafood_products': (int(seafood_products), ID_SEAFOOD),
            'fruits_vegetables': (int(fruits_vegetables), ID_FRUITSVEGETABLES),
            'frozen_food': (int(frozen_food), ID_FROZENFOOD),
            'pet_food': (int(pet_food), ID_PETFOOD)
    }
    
    for key in args.keys():
        session[FORM_DATA][key] = args[key]

    session.modified = True
    return redirect(url_for('miscellaneous'))

@app.route('/miscellaneous', methods=['GET'])
@login_required
def miscellaneous():
    html = render_template('form_steps/miscellaneous.html')
    response = make_response(html)
    return response

MISC_TYPES = ['computer_games', 'tobacco_products']

@app.route('/handler-misc', methods=['POST'])
@login_required
def handler_misc():
    computer_games = request.form.get('computer_games')
    tobacco_products = request.form.get('tobacco_products')
    
    args = {
        'computer_games': (int(computer_games), ID_SOFTWARE),
        'tobacco_products': (int(tobacco_products), ID_TOBACCO)
    }
    
    for key in args.keys():
        session[FORM_DATA][key] = args[key]
    
    session.modified = True
    return redirect(url_for('load_results'))

@app.route('/load-results')
@login_required
def load_results():
    # Increment submission count
    current_user.increment_submission_count()
    # Store result data from session into DB
    form_data_dict = session[FORM_DATA]
    
    # Store weekly travel
    for activity in DISTANCE_TYPES:
        if (activity not in form_data_dict) or (form_data_dict[activity] is None) or (form_data_dict[activity] == ""):
            continue
        km = form_data_dict[activity][0]
        if activity == "bike_distance" or activity == "walking_distance":
            emission_val = 0
        else:
            ret = dist_emissions(form_data_dict[activity][0], form_data_dict[activity][1], bypass_API=False)
            assert ret[1] == "kg"
            emission_val = round(ret[0] * 52, 2) #*52 for going from weekly to yearly cost
        current_user.add_weekly_travel(activity, emission_val, km)
        
    # Store long distance travel (flights)
    for origin_dist_pair in form_data_dict['flight']:
        activity = "flight"
        origin = origin_dist_pair[0]
        dest = origin_dist_pair[1]
        # accomodation = accomodation_list[i]
        emission = round(flight_emissions(origin, dest, bypass_API=False)[0], 2)
        current_user.add_long_distance_travel(activity, emission, origin, dest)
        
    # Store clothing
    for activity in CLOTHING_TYPES:
        if form_data_dict[activity] is None or form_data_dict[activity] == "":
            continue
        cost = form_data_dict[activity][0]
        activity_id = form_data_dict[activity][1]
        
        emission = round(cost_emissions(cost, activity_id, bypass_API=False)[0], 2)
        current_user.add_clothing(activity, emission, cost)
        
    # Store Food
    for activity in FOOD_TYPES:
        if form_data_dict[activity] is None or form_data_dict[activity] == "":
            continue
        cost = form_data_dict[activity][0]
        activity_id = form_data_dict[activity][1]
        
        emission = round(cost_emissions(cost, activity_id, bypass_API=False)[0], 2)
        emission_val = round(emission * 52, 2) # *52 for weekly to yearly
        current_user.add_food(activity, emission_val, cost)
        
    # Store Misc
    for activity in MISC_TYPES:
        if form_data_dict[activity] is None or form_data_dict[activity] == "":
            continue
        cost = form_data_dict[activity][0]
        activity_id = form_data_dict[activity][1]
        
        emission = round(cost_emissions(cost, activity_id, bypass_API=False)[0], 2)
        current_user.add_misc(activity, emission, cost)
    
    # Reset form data
    session.pop(FORM_DATA)
    return redirect(url_for('results'))

@app.route('/results', methods=['GET'])
@login_required
def results():
    
    this_username = request.args.get('username')
    if this_username == "" or this_username is None:
        this_user = current_user
    else:
        this_user = User.query.filter_by(username=this_username).first()
        
    #---Emissions Breakdown by Category
    total_emissions = [this_user.get_total_emissions(), 'total']
    weekly_travel_emissions = [this_user.get_weekly_travel_emissions(), 'weekly travel']
    long_distance_travel_emissions = [this_user.get_long_distance_travel_emissions(), 'long distance travel']
    clothing_emissions = [this_user.get_clothing_emissions(), 'clothing']
    food_emissions = [this_user.get_food_emissions(), 'food']
    misc_emissions = [this_user.get_misc_emissions(), 'misc']
    
    user_emissions_list = [total_emissions, weekly_travel_emissions, long_distance_travel_emissions,
                      clothing_emissions, food_emissions, misc_emissions]
    
    #---Calculating Max Category
    max_category = [0, 0]
    for category in user_emissions_list:
        # Skip total category when calculating max
        if category[1] == 'total':
            continue
        if category[0] >= max_category[0]:
            max_category = category
    if (total_emissions[0] == 0):
        max_category_percentage = 0
    else:
        max_category_percentage = round((max_category[0] / total_emissions[0]) * 100, 2)
    max_category.append(max_category_percentage)
            
    #---Comparison with other users    
    avg_total = 0
    avg_weekly_travel = 0
    avg_long_distance_travel = 0
    avg_clothing = 0
    avg_food = 0
    avg_misc = 0
    
    #--Calculate avg emissions for each category
    
    #Getting total emissions for each category
    all_users = User.query.all()
    user_count = len(all_users)
    
    #Check for first user ever:
    if user_count <= 1:
        html = render_template('results.html',                            
                           #First User
                           first_user=True,
                           user_emissions_list=user_emissions_list,
                           display_username=this_user.username)
        response = make_response(html)
        return response

    for user in all_users:
        avg_total += user.get_total_emissions()
        avg_weekly_travel += user.get_weekly_travel_emissions()
        avg_long_distance_travel += user.get_long_distance_travel_emissions()
        avg_clothing += user.get_clothing_emissions()
        avg_food += user.get_food_emissions()
        avg_misc += user.get_misc_emissions()
    
    avg_emissions_list = [avg_total, avg_weekly_travel, avg_long_distance_travel,
                        avg_clothing, avg_food, avg_misc]
    
    #Dividing by # of total users
    for i in range(len(avg_emissions_list)):
        avg_emissions_list[i] = round(avg_emissions_list[i]/user_count, 2)
    
    #Calculating difference in % btw user and avg emission for each category
    user_vs_avg_percentage_list = [] #[[23.34, 'total'], [5.12, 'weekly travel'], ......]
    for user, avg in zip(user_emissions_list, avg_emissions_list):
        # Account for 0 division (if user went from 0 in category)
        if avg == 0:
            avg = Decimal('0.00001')
        user_vs_avg_percentage_list.append([round(((user[0] - avg) / avg) * 100, 2), user[1]])
    
    event_list = this_user.get_individual_data()

    # Calculating User Emissions For Each Submission Number
    overtime_emission_set = []
    overtime_labels = []
    for i in range(1, this_user.submission_count+1):
        i_submission_emission = this_user.get_total_emissions(target_submission_number=i)
        overtime_labels.append(f"Submission #{i}")
        overtime_emission_set.append(i_submission_emission)
    
    html = render_template('results.html', 
                           #First User
                           first_user=False,
                           #Max Category
                           max_category=max_category,
                           max_category_percentage=max_category_percentage,
                           #User, Avg, User.vs.Avg Emission Lists
                           user_emissions_list=user_emissions_list,
                           avg_emissions_list=avg_emissions_list,
                           user_vs_avg_percentage_list=user_vs_avg_percentage_list,
                           event_list=event_list,
                           overtime_emission_set=overtime_emission_set,
                           overtime_labels=overtime_labels,
                           display_username=this_user.username)
    response = make_response(html)
    return response

#----------------------------------User Login/Signup----------------------------------------------------#

#User Auth
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    fetched_user = User.query.get(int(user_id))
    return fetched_user

# Redirect users to login if they try to access pages that require login
@login_manager.unauthorized_handler
def require_login():
    flash("Please register or login to access that page!")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        fetched_user = User.query.filter_by(username=username).first()
        if (fetched_user is None) or (password_hash != fetched_user.password_hash):
            flash('Username or password is incorrect.')
            return render_template('user_auth/login.html')
        else:
            login_user(fetched_user)
            return redirect(url_for('congrats'))
    elif request.method == 'GET':
        return render_template('user_auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(password) < 8 or not re.search('[^A-Za-z0-9]', password):
            flash('Password must be at least 8 characters long and contain at least one special character.')
            return redirect(url_for('register'))
    
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        

        try:
            new_user = User(username, password_hash)
            db.session.add(new_user)
            db.session.commit()
            flash('Account Created Successfully')
        except Exception:
            flash('Username already exists. Please try a different username.')
        return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('user_auth/register.html')

@app.route('/index')
@login_required
def congrats():
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
