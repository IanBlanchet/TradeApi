from xmlrpc.client import DateTime
from sqlalchemy.ext.declarative import declarative_base
from app.config import session, engine
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, backref
import pandas as pd
from datetime import *
from dateutil.parser import parse
import math

Base = declarative_base()


class Positions(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), index=True)
    gain = Column(Float)
    gain_can = Column(Float)
    risque = Column(Float)
    date_ouv = Column(Date)
    iv_ouv = Column(Float)
    prix_ouv = Column(Float)
    date_ferm = Column(Date)
    iv_ferm = Column(Float)
    prix_ferm = Column(Float)
    echeance = Column(Date)
    style = Column(String(10))
    strike = Column(Float)
    statut = Column(String(5))
    currency = Column(String(3))
    account = Column(String(10))
    contrats = relationship('Contrats', backref='position')
    titres = relationship('Titres', backref='position')
    
    def ratios(self):
        rendement = round((self.gain/self.risque)*100)
        rendement_ajust = round(self.gain/(self.strike*100))*100
        if self.date_ferm:
            rendement_annuel = (rendement/abs((self.date_ferm-self.date_ouv).days))*100
        else:
            rendement_annuel = None
        duree = abs((self.date_ferm-self.date_ouv).days)
        return duree, rendement, rendement_ajust, rendement_annuel

    def calcul_gain(self):
        gain_total = 0.0
        gain_total_can = 0.0
        for contrat in self.contrats:
            if contrat.montant:
                gain_total += contrat.montant
                gain_total_can += (contrat.montant * contrat.taux_change)
            if contrat.com:
                gain_total += contrat.com
                gain_total_can += (contrat.com * contrat.taux_change)
        for titre in self.titres:
            if titre.montant:
                gain_total += titre.montant
                gain_total_can += (titre.montant * titre.taux_change)
            if titre.com:
                gain_total += titre.com
                gain_total_can += (titre.com * titre.taux_change)
        self.gain = gain_total
        self.gain_can = gain_total_can
        return gain_total
    
    def close_pos(self):
        self.statut = 'Close'
        date_contrat = []
        for contrat in self.contrats:
            if contrat.date:
                date_contrat.append(contrat.date)
        for titre in self.titres:
            if titre.date:
                date_contrat.append(titre.date)
        
        self.date_ferm = max(date_contrat)
        
        historique_df = pd.read_excel('../historique.xlsx')
        historique_df = historique_df[historique_df.ticker == self.ticker]
        try:
            self.prix_ouv = historique_df[historique_df.Date == str(self.date_ouv)].iloc[0]['prix(close)']
            self.prix_ferm = historique_df[historique_df.Date == str(self.date_ferm)].iloc[0]['prix(close)']
            self.iv_ouv = historique_df[historique_df.Date == str(self.date_ouv)].iloc[0]['IV(close)']
            self.iv_ferm = historique_df[historique_df.Date == str(self.date_ferm)].iloc[0]['IV(close)']
        except:
            self.prix_ouv = None
            self.prix_ferm = None
            self.iv_ouv = None
            self.iv_ferm = None
        
        

    def set_strike(self):
        list_strike = []
        for contrat in self.contrats:
            list_strike.append(contrat.strike)
        max_strike = max(list_strike)
        min_strike = min(list_strike)
        self.strike = max_strike
        if self.style == 'Vertical':
            self.risque = (max_strike - min_strike)*100
        else :
            self.risque = max_strike*100*0.4



class Contrats(Base):
    __tablename__ = "contrats"
    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey('positions.id'))
    montant = Column(Float)
    com = Column(Float)
    side = Column(String(4)) #put ou call
    transaction = Column(Integer)#-1 sell 1 buy
    echeance = Column(Date)
    strike = Column(Float)
    date = Column(Date)
    ticker = Column(String(10))
    taux_change = Column(Float)
    currency = Column(String(3))


class Titres(Base):
    __tablename__ = "titres"
    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey('positions.id'))
    montant = Column(Float)
    com = Column(Float)
    transaction = Column(Integer)#-100 sell 100 buy
    date = Column(Date)
    ticker = Column(String(10))
    taux_change = Column(Float)
    currency = Column(String(3))


Base.metadata.create_all(engine)