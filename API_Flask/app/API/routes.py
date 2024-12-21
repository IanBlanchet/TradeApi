from flask.wrappers import Request
from app.API import bp
from app.models import Titres, Positions, Contrats, Base
from app import app
from app.config import session, engine
import pandas as pd
from flask_restful import Resource, Api, abort
from datetime import datetime, timedelta
#from flask_sqlalchemy import SQLAlchemy
#import sqlalchemy
import json
from flask import Response, request
from flask_marshmallow import Marshmallow
from app.API.schemas import PositionsSchema, ContratsSchema, TitresSchema

api = Api(app)



#cont = session.query(Contrats).filter_by(id=2857).first()
#session.delete(cont)
#session.commit()
#titre = session.query(Titres).all()

# Serialize the data for the response
positions_schema = PositionsSchema(many=True)
contrats_schema = ContratsSchema(many=True)
titres_schema = TitresSchema(many=True)
contrat_schema = ContratsSchema()
titre_schema = TitresSchema()

mesTransactions = pd.read_excel('../transactions.xlsx')
mesTransactions.fillna('', inplace=True)
mesTransactions.reset_index(inplace=True)
mesTransactions = mesTransactions.rename(columns={
    'underlyingSymbol': 'ticker', 'tradeDate': 'date',
    'netCash':'montant','ibCommission' :'com',
    'putCall':'side','quantity':'transaction', 
    'expiry':'echeance', 'fxRateToBase':'taux_change'    
    })
mesTransactions = mesTransactions[mesTransactions.date > (datetime.today()-timedelta(9))]
dictTransactions = mesTransactions.to_json(orient='records', date_format='iso')

position653 = session.query(Positions).filter_by(id = 653).first()
position653.calcul_gain()
session.commit()


class PositionsApi(Resource):
    def get(self):
        if request.args.get('ticker'):
            pos = session.query(Positions).filter_by(ticker=request.args.get('ticker'))
            return positions_schema.dump(pos)
        pos = session.query(Positions).all()
        return positions_schema.dump(pos)

    def post(self):
        data = request.get_json(force=True)
        laPosition = session.query(Positions).filter_by(id = data['id']).first()
        laPosition.close_pos()
        session.commit()
        return data


class ContratsApi(Resource):
    def get(self):        
        if request.args.get('position_id'):
            cont = session.query(Contrats).filter_by(position_id=request.args.get('position_id')).all()
            return contrats_schema.dump(cont)
        cont = session.query(Contrats).all()
        return contrats_schema.dump(cont)

    def post(self):
        data = request.get_json(force=True)
        contratsAjout = contrats_schema.load(data['data'])
        if data.get('position'):
            contratRef = contratsAjout[0]
            nouvellePosition = Positions(
                                        ticker=contratRef.ticker,
                                        date_ouv=contratRef.date,
                                        echeance=contratRef.echeance,
                                        statut='Open',
                                        currency=contratRef.currency,
                                        account=data.get('accountId'),
                                        style=data.get('typePosition')
            )
            session.add(nouvellePosition)
            session.commit()
            for contrat in contratsAjout:
                contrat.position_id = nouvellePosition.id
                session.add(contrat)
                session.commit()
            nouvellePosition.calcul_gain()
            nouvellePosition.set_strike()
            session.commit()
            return data
        for contrat in contratsAjout:
            session.add(contrat)
            session.commit()
        positionId = contratsAjout[0].position_id
        laPosition = session.query(Positions).filter_by(id = positionId).first()
        laPosition.calcul_gain()
        session.commit()
        return data
            
      

class TitresApi(Resource):
    def get(self):
        if request.args.get('position_id'):
            titre = session.query(Titres).filter_by(position_id=request.args.get('position_id')).all()
            return titres_schema.dump(titre)
        titre = session.query(Titres).all()
        return titres_schema.dump(titre)
    
    def post(self):
        data = request.get_json(force=True)        
        titresAjout = titres_schema.load(data['data'])
        
        for titre in titresAjout:
            session.add(titre)
            session.commit()
        positionId = titresAjout[0].position_id
        laPosition = session.query(Positions).filter_by(id = positionId).first()
        laPosition.calcul_gain()
        session.commit()
        return data
        

class TransactionsApi(Resource):
    def get(self):
        return Response(dictTransactions, mimetype='application/json')


api.add_resource(PositionsApi, '/api/v1/positions')
api.add_resource(TransactionsApi, '/api/v1/transactions')
api.add_resource(ContratsApi, '/api/v1/contrats')
api.add_resource(TitresApi, '/api/v1/titres')