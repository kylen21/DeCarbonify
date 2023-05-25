from config import app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100))
    submission_count = db.Column(db.Integer, nullable=False)
    
    weekly_travel_list = db.relationship('WeeklyTravel')
    long_distance_travel_list = db.relationship('LongDistanceTravel')
    clothing_list = db.relationship('Clothing')
    food_list = db.relationship('Food')
    misc_list = db.relationship('Misc')
    
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash
        self.submission_count = 0
        
        self.weekly_travel_list = []
        self.long_distance_travel_list = []
        self.clothing_list = []
        self.food = []
        
    def __lt__(self, other):
        return self.get_total_emissions() < other.get_total_emissions()
        
    def get_total_emissions(self, target_submission_number=None):
        total = 0
        # Getting specific submission number
        if target_submission_number is None:
            total += self.get_weekly_travel_emissions()
            total += self.get_long_distance_travel_emissions()
            total += self.get_clothing_emissions()
            total += self.get_food_emissions()
            total += self.get_misc_emissions()  
        # Getting latest submission number
        else:
            total += self.get_weekly_travel_emissions(target_submission_number=target_submission_number)
            total += self.get_long_distance_travel_emissions(target_submission_number=target_submission_number)
            total += self.get_clothing_emissions(target_submission_number=target_submission_number)
            total += self.get_food_emissions(target_submission_number=target_submission_number)
            total += self.get_misc_emissions(target_submission_number=target_submission_number)
        return total
    
    def get_weekly_travel_emissions(self, target_submission_number=None):
        if target_submission_number is None:
            submission_num = self.submission_count
        else:
            submission_num = target_submission_number
        event_list = [event.emission for event in self.weekly_travel_list if event.submission_number == submission_num]
        return round(sum(event_list), 2)

    
    def get_long_distance_travel_emissions(self, target_submission_number=None):
        if target_submission_number is None:
            submission_num = self.submission_count
        else:
            submission_num = target_submission_number
        event_list = [event.emission for event in self.long_distance_travel_list if event.submission_number == submission_num]
        return round(sum(event_list), 2)
    
    def get_clothing_emissions(self, target_submission_number=None):
        if target_submission_number is None:
            submission_num = self.submission_count
        else:
            submission_num = target_submission_number
        event_list = [event.emission for event in self.clothing_list if event.submission_number == submission_num]
        return round(sum(event_list), 2)
    
    def get_food_emissions(self, target_submission_number=None):
        if target_submission_number is None:
            submission_num = self.submission_count
        else:
            submission_num = target_submission_number
        event_list = [event.emission for event in self.food_list if event.submission_number == submission_num]
        return round(sum(event_list), 2)
            
    def get_misc_emissions(self, target_submission_number=None):
        if target_submission_number is None:
            submission_num = self.submission_count
        else:
            submission_num = target_submission_number
        event_list = [event.emission for event in self.misc_list if event.submission_number == submission_num]
        return round(sum(event_list), 2)

    def get_individual_data(self, target_submission_number=None):
        if target_submission_number is None:
            submission_num = self.submission_count
        else:
            submission_num = target_submission_number
        event_list = {"Weekly Travel":[], "Long Distance Travel":[], "Clothing":[], "Food":[], "Misc":[]}
        event_list["Weekly Travel"].append([event.emission for event in self.weekly_travel_list if event.submission_number == submission_num]) 
        event_list["Long Distance Travel"].append([event.emission for event in self.long_distance_travel_list if event.submission_number == submission_num]) 
        event_list["Clothing"].append([event.emission for event in self.clothing_list if event.submission_number == submission_num]) 
        event_list["Food"].append([event.emission for event in self.food_list if event.submission_number == submission_num]) 
        event_list["Misc"].append([event.emission for event in self.misc_list if event.submission_number == submission_num]) 

        return event_list

    
    def increment_submission_count(self):
        self.submission_count += 1
        db.session.commit()
        
    def add_weekly_travel(self, activity, emission, km):
        wt = WeeklyTravel(self.submission_count, activity, emission, km)
        self.weekly_travel_list.append(wt)
        db.session.add(wt)
        db.session.commit()
    
    def add_long_distance_travel(self, activity, emission, origin, dest):
        ldt = LongDistanceTravel(self.submission_count, activity, emission, origin, dest)
        self.long_distance_travel_list.append(ldt)
        db.session.add(ldt)
        db.session.commit()
        
    def add_clothing(self, activity, emission, cost):
        c = Clothing(self.submission_count, activity, emission, cost)
        self.clothing_list.append(c)
        db.session.add(c)
        db.session.commit()
        
    def add_food(self, activity, emission, cost):
        f = Food(self.submission_count, activity, emission, cost)
        self.food_list.append(f)
        db.session.add(f)
        db.session.commit()
        
    def add_misc(self, activity, emission, cost):
        m = Misc(self.submission_count, activity, emission, cost)
        self.misc_list.append(m)
        db.session.add(m)
        db.session.commit()
        

class Category(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    submission_number = db.Column(db.Integer, nullable=False)
    activity = db.Column(db.String, nullable=False) 
    emission = db.Column(db.Numeric, nullable=False)
    
    def __init__(self, submission_number, activity, emission):
        self.submission_number = submission_number
        self.activity = activity
        self.emission = emission

class WeeklyTravel(Category):
    __tablename__ = "weekly_travel"
        
    km = db.Column(db.Numeric, nullable=False)
    
    def __init__(self, submission_number, activity, emission, km):
        super().__init__(submission_number, activity, emission)
        self.km = km
    
class LongDistanceTravel(Category):
    __tablename__ = "long_distance_travel"
        
    origin = db.Column(db.String, nullable=False)
    dest = db.Column(db.String, nullable=False)
    
    def __init__(self, submission_number, activity, emission, origin, dest):
        super().__init__(submission_number, activity, emission)
        self.origin = origin
        self.dest = dest
    
class Clothing(Category):
    __tablename__ = "clothing"
    
    cost = db.Column(db.Numeric, nullable=False)
    
    def __init__(self, submission_number, activity, emission, cost):
        super().__init__(submission_number, activity, emission)
        self.cost = cost

class Food(Category):
    __tablename__ = "food"
    
    cost = db.Column(db.Numeric, nullable=False)
    
    def __init__(self, submission_number, activity, emission, cost):
        super().__init__(submission_number, activity, emission)
        self.cost = cost
        
class Misc(Category):
    __tablename__ = "misc"
    
    cost = db.Column(db.Numeric, nullable=False)
    
    def __init__(self, submission_number, activity, emission, cost):
        super().__init__(submission_number, activity, emission)
        self.cost = cost
    
def insert_dummy_user(username):
    with app.app_context():
        pass
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()