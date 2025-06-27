from src.models import db
from datetime import datetime

class Motorista(db.Model):
    __tablename__ = 'motoristas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    matricula = db.Column(db.String(20))
    funcao = db.Column(db.String(50))
    admissao = db.Column(db.Date)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'matricula': self.matricula,
            'funcao': self.funcao,
            'admissao': self.admissao.isoformat() if self.admissao else None,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Motorista {self.nome}>'

