from flask import Blueprint

bp = Blueprint('API', __name__,template_folder='templates')


from app.API import routes
