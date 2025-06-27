from src.models import db
from datetime import datetime

class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), nullable=False, unique=True)
    identificador = db.Column(db.String(20))
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'))
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    motorista = db.relationship('Motorista', backref='veiculos_associados')
    
    def to_dict(self):
        motorista_dict = None
        if self.motorista:
            motorista_dict = {
                'id': self.motorista.id,
                'nome': self.motorista.nome,
                'cpf': self.motorista.cpf,
                'matricula': self.motorista.matricula
            }
        
        return {
            'id': self.id,
            'placa': self.placa,
            'identificador': self.identificador,
            'motorista_id': self.motorista_id,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'motorista': motorista_dict
        }
    
    def __repr__(self):
        return f'<Veiculo {self.placa}>'

