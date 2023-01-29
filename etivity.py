from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Index, ForeignKey, UniqueConstraint, Integer, String, Enum, Date, Text, Time, func
from sqlalchemy.dialects.mysql import CHAR, FLOAT, INTEGER, TINYINT
from sqlalchemy.orm import declarative_base, relationship, sessionmaker 

engine = create_engine('mysql+mysqlconnector://root:framysql021@localhost/noleggio', echo = True)

Base = declarative_base()


class Cliente(Base): 
    __tablename__ = 'Cliente'
    CodiceFiscale = Column(String(16), primary_key = True) 
    Email = Column(String(255), nullable = False, unique = True)
    TipoCliente = Column(Enum('Privato','Azienda'), nullable = False)
    Nome = Column(String(50))
    Cognome = Column(String(50))
    DataNascita = Column(Date)
    LuogoNascita = Column(String(50))
    Sesso = Column(Enum('M','F'))
    RagioneSociale = Column(String(255))
    Indirizzo = Column(String(255))
    Città = Column(String(50))
    Provincia = Column(CHAR(2))
    CAP = Column(CHAR(5))
    PartitaIVA = Column(CHAR(11))
    Index('cognome_nome_index', Cognome, Nome)
    Index('citta_index', Città)
    Index('prov_index', Provincia)
    contratti = relationship(
        'Contratto', 
        order_by = 'Contratto.CodiceContratto', 
        back_populates = 'cliente',
        cascade = 'all, delete-orphan'
        )


class Categoria(Base): 
    __tablename__ = 'Categoria'
    CodiceCategoria = Column(CHAR(3), primary_key = True) 
    Nome = Column(String(50), nullable = False, unique = True)
    modelli = relationship('Modello', order_by = 'Modello.CodiceModello', back_populates = 'categoria')


class Marca(Base): 
    __tablename__ = 'Marca'
    CodiceMarca = Column(CHAR(3), primary_key = True) 
    Nome = Column(String(50), nullable = False, unique = True)
    modelli = relationship('Modello', order_by = 'Modello.CodiceModello', back_populates = 'marca')


class Modello(Base): 
    __tablename__ = 'Modello'
    CodiceModello = Column(CHAR(3), primary_key = True) 
    CodiceMarca = Column(CHAR(3), ForeignKey(Marca.CodiceMarca, onupdate = 'CASCADE'), nullable = False)
    CodiceCategoria = Column(CHAR(3), ForeignKey(Categoria.CodiceCategoria, onupdate = 'CASCADE'), nullable = False)
    Nome = Column(String(50), nullable = False, unique = True)
    Descrizione = Column(Text)
    PrezzoGg = Column(FLOAT(precision = 10, scale = 2, unsigned = True), nullable = False)
    marca = relationship('Marca', back_populates = 'modelli')
    categoria = relationship('Categoria', back_populates = 'modelli')
    veicoli = relationship('Veicolo', order_by = 'Veicolo.Targa', back_populates = 'modello')
    extra = relationship('ExtraModello', back_populates = 'modello')


class Veicolo(Base): 
    __tablename__ = 'Veicolo'
    Targa = Column(CHAR(7), primary_key = True) 
    CodiceModello = Column(CHAR(3), ForeignKey(Modello.CodiceModello, onupdate = 'CASCADE'), nullable = False)
    Km = Column(INTEGER(unsigned = True), nullable = False)
    Dannivisibili = Column(Text)
    modello = relationship('Modello', back_populates = 'veicoli')
    contratti = relationship('Contratto', order_by = 'Contratto.CodiceContratto', back_populates = 'veicolo')


class Sede(Base): 
    __tablename__ = 'Sede'
    CodiceSede = Column(CHAR(3), primary_key = True) 
    Indirizzo = Column(String(255), nullable = False)
    CAP = Column(CHAR(5), nullable = False)
    Città = Column(String(50), nullable = False)
    Provincia = Column(CHAR(2), nullable = False)
    UniqueConstraint(Indirizzo, Città, Provincia, name = 'Indirizzo')
    contratti_ritiro = relationship('Contratto', primaryjoin = 'Contratto.CodiceSedeRitiro == Sede.CodiceSede', order_by = 'Contratto.CodiceContratto', back_populates = 'sede_ritiro')
    contratti_consegna = relationship('Contratto', primaryjoin = 'Contratto.CodiceSedeConsegna == Sede.CodiceSede', order_by = 'Contratto.CodiceContratto', back_populates = 'sede_consegna')


class Extra(Base): 
    __tablename__ = 'Extra'
    CodiceExtra = Column(CHAR(3), primary_key = True) 
    Nome = Column(String(50), nullable = False, unique = True)
    modelli = relationship('ExtraModello', back_populates = 'extra')
    contratti = relationship('ExtraContratto', back_populates = 'extra')


class ExtraModello(Base):
    __tablename__ = 'ExtraModello'
    CodiceExtra = Column(ForeignKey(Extra.CodiceExtra, onupdate = 'CASCADE', ondelete = 'CASCADE'), primary_key = True)
    CodiceModello = Column(ForeignKey(Modello.CodiceModello, onupdate = 'CASCADE', ondelete = 'CASCADE'), primary_key = True)
    Prezzo = Column(FLOAT(precision = 10, scale = 2, unsigned = True), nullable = False)
    modello = relationship('Modello', back_populates = 'extra')
    extra = relationship('Extra', back_populates = 'modelli')


class Contratto(Base): 
    __tablename__ = 'Contratto'
    CodiceContratto = Column(CHAR(6), primary_key = True) 
    CodiceFiscale = Column(String(16), ForeignKey(Cliente.CodiceFiscale, onupdate = 'CASCADE', ondelete = 'CASCADE'), nullable = False) 
    Targa = Column(CHAR(7), ForeignKey(Veicolo.Targa, onupdate = 'CASCADE'), nullable = False)
    CodiceSedeRitiro = Column(CHAR(3), ForeignKey(Sede.CodiceSede, onupdate = 'CASCADE'), nullable = False) 
    CodiceSedeConsegna = Column(CHAR(3), ForeignKey(Sede.CodiceSede, onupdate = 'CASCADE'), nullable = False) 
    DataFirma = Column(Date, nullable = False)
    DataRitiro = Column(Date, nullable = False)
    OraRitiro = Column(Time, nullable = False)
    DataConsegna = Column(Date, nullable = False)
    OraConsegna = Column(Time, nullable = False)
    KmRitiro = Column(INTEGER(unsigned = True))
    KmConsegna = Column(INTEGER(unsigned = True))  
    DanniVisibiliRitiro = Column(Text)
    DanniVisibiliConsegna = Column(Text)
    PrezzoBaseNoleggio = Column(FLOAT(precision = 10, scale = 2, unsigned = True), nullable = False)
    Index('dt_consegna_index', DataConsegna)
    Index('dt_ritiro_index', DataRitiro)
    cliente = relationship('Cliente', back_populates = 'contratti')
    veicolo = relationship('Veicolo', back_populates = 'contratti')
    sede_ritiro = relationship('Sede', primaryjoin = 'Contratto.CodiceSedeRitiro == Sede.CodiceSede', back_populates = 'contratti_ritiro')
    sede_consegna = relationship('Sede', primaryjoin = 'Contratto.CodiceSedeConsegna == Sede.CodiceSede', back_populates = 'contratti_consegna')
    extra = relationship('ExtraContratto', back_populates = 'contratto', cascade = 'all, delete-orphan')
    conducenti = relationship('Conducente', secondary = 'ConducenteContratto', back_populates = 'contratti')
    

class ExtraContratto(Base):
    __tablename__ = 'ExtraContratto'
    CodiceExtra = Column(ForeignKey(Extra.CodiceExtra, onupdate = 'CASCADE'), primary_key = True)
    CodiceContratto = Column(ForeignKey(Contratto.CodiceContratto, onupdate = 'CASCADE'), primary_key = True)
    Quantità = Column(TINYINT(unsigned = True), nullable = False)
    Prezzo = Column(FLOAT(precision = 10, scale = 2, unsigned = True), nullable = False)
    contratto = relationship('Contratto', back_populates = 'extra')
    extra = relationship('Extra', back_populates = 'contratti')


class Conducente(Base): 
    __tablename__ = 'Conducente'
    CodiceFiscaleConducente = Column(String(16), primary_key = True) 
    Nome = Column(String(50), nullable = False)
    Cognome = Column(String(50), nullable = False)
    DataNascita = Column(Date, nullable = False)
    LuogoNascita = Column(String(50), nullable = False)
    Sesso = Column(Enum('M','F'), nullable = False)
    NumeroPatente = Column(String(20), nullable = False)
    DataScadenzaPatente = Column(Date, nullable = False)
    Index('cognome_nome_index', Cognome, Nome)
    Index('n_pat_index', NumeroPatente)
    Index('sc_pat_index', DataScadenzaPatente)
    contratti = relationship('Contratto', secondary = 'ConducenteContratto', back_populates = 'conducenti')


ConducenteContratto = Table('ConducenteContratto', Base.metadata, 
    Column('CodiceFiscaleConducente', ForeignKey(Conducente.CodiceFiscaleConducente, onupdate = 'CASCADE'), primary_key = True), 
    Column('CodiceContratto', ForeignKey(Contratto.CodiceContratto, onupdate = 'CASCADE', ondelete = 'CASCADE'), primary_key = True)
)

Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine)
session = Session()

#INSERIMENTO

categorie = [
    Categoria(CodiceCategoria = 'BER', Nome = 'Berlina'),
    Categoria(CodiceCategoria = 'SUV', Nome = 'SUV'),
    Categoria(CodiceCategoria = 'MOT', Nome = 'Motociclo'),
    Categoria(CodiceCategoria = 'COU', Nome = 'Coupé')
]
session.add_all(categorie)

marche = [
    Marca(CodiceMarca = 'BMW', Nome = 'Bmw'),
    Marca(CodiceMarca = 'AUD', Nome = 'Audi'),
    Marca(CodiceMarca = 'MER', Nome = 'Mercedes'),
    Marca(CodiceMarca = 'HON', Nome = 'Honda')
]
session.add_all(marche)

modelli = [
    Modello(CodiceModello = '001', CodiceMarca = 'BMW', Nome = 'X1', CodiceCategoria = 'SUV', PrezzoGg = 180.00),
    Modello(CodiceModello = '002', CodiceMarca = 'BMW', Nome = 'X5', CodiceCategoria = 'SUV', PrezzoGg = 300.00),
    Modello(CodiceModello = '003', CodiceMarca = 'AUD', Nome = 'A4', CodiceCategoria = 'BER', PrezzoGg = 270.00),
    Modello(CodiceModello = '004', CodiceMarca = 'MER', Nome = 'Classe C', CodiceCategoria = 'BER', PrezzoGg = 290.00),
    Modello(CodiceModello = '005', CodiceMarca = 'HON', Nome = 'SH150', CodiceCategoria = 'MOT', PrezzoGg = 90.00),
]
session.add_all(modelli)

extra = [
    Extra(
        CodiceExtra = 'E01', 
        Nome = 'Azzeramento franchigie',
        modelli = [
            ExtraModello(CodiceModello = '001', Prezzo = 100),
            ExtraModello(CodiceModello = '002', Prezzo = 200),
            ExtraModello(CodiceModello = '003', Prezzo = 150),
            ExtraModello(CodiceModello = '004', Prezzo = 170),
            ExtraModello(CodiceModello = '005', Prezzo = 190)
        ]
    ),
    Extra(
        CodiceExtra = 'E02', 
        Nome = 'Franchigia incidente',
        modelli = [
            ExtraModello(CodiceModello = '001', Prezzo = 200),
            ExtraModello(CodiceModello = '002', Prezzo = 400),
            ExtraModello(CodiceModello = '003', Prezzo = 300),
            ExtraModello(CodiceModello = '004', Prezzo = 350),
            ExtraModello(CodiceModello = '005', Prezzo = 375)
        ]
    )
]
session.add_all(extra)

sedi = [
    Sede(CodiceSede = 'S01', Indirizzo = 'Via Cavour, 100', CAP = '00184', Città = 'Roma', Provincia = 'RM'),
    Sede(CodiceSede = 'S02', Indirizzo = 'Viale Parioli, 12', CAP = '00197', Città = 'Roma', Provincia = 'RM'),
]
session.add_all(sedi)

v1 = Veicolo(Targa = 'AG547PW', Km = 5000)
v1.modello = Modello(CodiceModello = '006', Nome = '500', PrezzoGg = 100.00)
v1.modello.categoria = Categoria(CodiceCategoria = 'UTI', Nome = 'Utilitaria')
v1.modello.marca = Marca(CodiceMarca = 'FIA', Nome = 'Fiat')
v1.modello.extra = [
    ExtraModello(CodiceExtra = 'E01', Prezzo = 50),
    ExtraModello(CodiceExtra = 'E02', Prezzo = 110),
]

session.add(v1)

c1 = Contratto(
    CodiceContratto = '230001',
    Targa = 'AG547PW',
    CodiceSedeRitiro = 'S01',
    CodiceSedeConsegna = 'S02',
    DataFirma = '2023-01-10',
    DataRitiro = '2023-01-15',
    OraRitiro = '10:30:00',
    DataConsegna = '2023-01-20',
    OraConsegna = '21:00:00',
    KmRitiro = 200,
    KmConsegna = 587,
    PrezzoBaseNoleggio = 500
)

c1.cliente = Cliente(
    CodiceFiscale = 'CLNFNC75D13H501Q',
    Email = 'test@mail.com',
    TipoCliente = 'Privato',
    Cognome = 'Colangeli',
    Nome = 'Francesco',
    DataNascita = '1975-04-13',
    LuogoNascita = 'Roma',
    Sesso = 'M' 
)

c1.extra = [
    ExtraContratto(CodiceExtra = 'E01', Quantità = 1, Prezzo = 50)
]

c1.conducenti = [
    Conducente(
        CodiceFiscaleConducente = 'CLNFNC75D13H501Q',
        Cognome = 'Colangeli',
        Nome = 'Francesco',
        DataNascita = '1975-04-13',
        LuogoNascita = 'Roma',
        Sesso = 'M',
        NumeroPatente = 'AJ7806541',
        DataScadenzaPatente = '2025-01-19'
    )
]
session.add(c1)  

session.commit()

#LETTURA
#Elenco Clienti di tipo privato
result = session.query(Cliente).filter(Cliente.TipoCliente == 'Privato').all()

#Codice Fiscale Clienti e Numero contratti sottoscritti con prezzo base noleggio uguale o superiore a 250 euro
result = session.query(Cliente.CodiceFiscale, func.count(Contratto.CodiceContratto)).join(Contratto).filter(Contratto.PrezzoBaseNoleggio >= 250).group_by(Cliente.CodiceFiscale).all()


#AGGIORNAMENTO
#aggiornamento data scadenza conducente
c1 = session.query(Conducente).get('CLNFNC75D13H501Q')
c1.DataScadenzaPatente = '2030-01-01'
session.add(c1)


#ELIMINAZIONE 
#eliminazione cliente (elimina anche contratti e extra contratto collegati)
c1 = session.query(Cliente).get('CLNFNC75D13H501Q')
session.delete(c1)