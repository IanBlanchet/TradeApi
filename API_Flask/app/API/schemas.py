from app.models import Positions, Contrats, Titres
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import post_load, INCLUDE, EXCLUDE, fields
from app.config import session
from app import app
import dateutil
import pytz

myTimezone = pytz.timezone('America/New_York')

ma = Marshmallow(app)


class PositionsSchema(ma.Schema):
    class Meta:
        model = Positions
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('id','ticker', 'gain', 'statut', 'symbol', 'strike', 'style', 'account')
    
    @post_load
    def make_position(self, data, **kwargs):
        return Positions(**data)



class ContratsSchema(ma.Schema):
    class Meta:
        model = Contrats
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('montant', 'side', 'transaction',
                    'strike', 'ticker', 'echeance',
                    'position_id', 'com', 'date',
                    'taux_change', 'currency')

    @post_load
    def make_contrat(self, data, **kwargs):
        return Contrats(**data)


class TitresSchema(ma.Schema):
    class Meta:
        model = Titres
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('montant', 'transaction',
                    'ticker', 'position_id', 'com', 'date',
                    'taux_change', 'currency')
    @post_load
    def make_titre(self, data, **kwargs):
        return Titres(**data)



'''
class ContratsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Contrats
        include_fk = True
        #sqla_session = session
        #fields = ('montant', 'side', 'transaction', 'strike', 'ticker', 'echeance', 'position_id') 
        unknown = EXCLUDE
    #echeance = fields.NaiveDateTime(timezone=myTimezone)
    echeance = auto_field()
    #date = fields.DateTime()
    date = auto_field()

    @post_load
    def make_contrat(self, data, **kwargs):
        return Contrats(**data)

class TitresSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Titres
        include_fk = True
        unknown = EXCLUDE
        #sqla_session = session
        #fields = ('montant', 'transaction', 'ticker', 'date')
    date = fields.DateTime()

    @post_load
    def make_titre(self, data, **kwargs):
        return Titres(**data)'''



