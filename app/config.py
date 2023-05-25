from flask import Flask

app = Flask(__name__)
#SQLAlchemy Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#Testing
# app.config['LOGIN_DISABLED'] = True

