from api import flight_emissions
from db import db, User
from config import app
from constants import *
from api import dist_emissions

if __name__ == "__main__":
    with app.app_context():
        ret = dist_emissions(33, '9e3e1d32-9158-44fa-967b-01dd4eded999', bypass_API=False)
        print(ret)
