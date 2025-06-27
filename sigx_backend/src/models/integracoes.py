from src.models import db
from datetime import datetime

class IntegracaoAbastecimento(db.Model):
    __tablename__ = 'integracao_abastecimento'
    
    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    posto = db.Column(db.String(100))
    endereco = db.Column(db.Text)
    litros = db.Column(db.Numeric(8, 2))
    valor = db.Column(db.Numeric(10, 2))
    evento_jornada_id = db.Column(db.Integer, db.ForeignKey('eventos_jornada.id'))
    processado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    veiculo = db.relationship('Veiculo', backref='abastecimentos')
    evento_jornada = db.relationship('EventoJornada', backref='abastecimento', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'veiculo_id': self.veiculo_id,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'posto': self.posto,
            'endereco': self.endereco,
            'litros': float(self.litros) if self.litros else None,
            'valor': float(self.valor) if self.valor else None,
            'evento_jornada_id': self.evento_jornada_id,
            'processado': self.processado,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class IntegracaoChecklist(db.Model):
    __tablename__ = 'integracao_checklist'
    
    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    tipo_checklist = db.Column(db.String(50))  # 'saida', 'chegada', 'manutencao'
    status = db.Column(db.String(20))  # 'aprovado', 'reprovado', 'pendente'
    observacoes = db.Column(db.Text)
    evento_jornada_id = db.Column(db.Integer, db.ForeignKey('eventos_jornada.id'))
    processado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    veiculo = db.relationship('Veiculo', backref='checklists')
    motorista = db.relationship('Motorista', backref='checklists')
    evento_jornada = db.relationship('EventoJornada', backref='checklist', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'veiculo_id': self.veiculo_id,
            'motorista_id': self.motorista_id,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'tipo_checklist': self.tipo_checklist,
            'status': self.status,
            'observacoes': self.observacoes,
            'evento_jornada_id': self.evento_jornada_id,
            'processado': self.processado,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class IntegracaoManutencao(db.Model):
    __tablename__ = 'integracao_manutencao'
    
    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    tipo_manutencao = db.Column(db.String(50))  # 'preventiva', 'corretiva', 'revisao'
    descricao = db.Column(db.Text)
    oficina = db.Column(db.String(100))
    endereco = db.Column(db.Text)
    evento_jornada_id = db.Column(db.Integer, db.ForeignKey('eventos_jornada.id'))
    processado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    veiculo = db.relationship('Veiculo', backref='manutencoes')
    evento_jornada = db.relationship('EventoJornada', backref='manutencao', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'veiculo_id': self.veiculo_id,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'tipo_manutencao': self.tipo_manutencao,
            'descricao': self.descricao,
            'oficina': self.oficina,
            'endereco': self.endereco,
            'evento_jornada_id': self.evento_jornada_id,
            'processado': self.processado,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

