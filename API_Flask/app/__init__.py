from app.config import Config
from app.config import session, Base, engine
from app.models import Positions, Contrats, Titres
import psycopg2
from flask import Flask
from flask_cors import CORS
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView





#l'application FLASK
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
admin = Admin(app, name='API_Flask', template_mode='bootstrap4')
admin.add_view(ModelView(Positions, session))
admin.add_view(ModelView(Contrats, session))


from app.API import bp as API_bp
app.register_blueprint(API_bp)



