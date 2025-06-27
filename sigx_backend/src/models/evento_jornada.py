from src.models import db
from datetime import datetime

class EventoJornada(db.Model):
    __tablename__ = 'eventos_jornada'
    
    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=False)
    tipo_evento_id = db.Column(db.Integer, db.ForeignKey('tipos_evento.id'), nullable=False)
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime)
    duracao_minutos = db.Column(db.Integer)
    latitude_inicio = db.Column(db.Numeric(10, 8))
    longitude_inicio = db.Column(db.Numeric(11, 8))
    latitude_fim = db.Column(db.Numeric(10, 8))
    longitude_fim = db.Column(db.Numeric(11, 8))
    endereco_inicio = db.Column(db.Text)
    endereco_fim = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    classificacao_automatica = db.Column(db.Boolean, default=False)
    aprovado = db.Column(db.Boolean, default=False)
    usuario_aprovacao = db.Column(db.String(50))
    data_aprovacao = db.Column(db.DateTime)
    sincronizado_sigx = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    veiculo = db.relationship('Veiculo', backref='eventos')
    motorista = db.relationship('Motorista', backref='eventos')
    tipo_evento = db.relationship('TipoEvento', backref='eventos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'veiculo_id': self.veiculo_id,
            'motorista_id': self.motorista_id,
            'tipo_evento_id': self.tipo_evento_id,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'duracao_minutos': self.duracao_minutos,
            'latitude_inicio': float(self.latitude_inicio) if self.latitude_inicio else None,
            'longitude_inicio': float(self.longitude_inicio) if self.longitude_inicio else None,
            'latitude_fim': float(self.latitude_fim) if self.latitude_fim else None,
            'longitude_fim': float(self.longitude_fim) if self.longitude_fim else None,
            'endereco_inicio': self.endereco_inicio,
            'endereco_fim': self.endereco_fim,
            'observacoes': self.observacoes,
            'classificacao_automatica': self.classificacao_automatica,
            'aprovado': self.aprovado,
            'usuario_aprovacao': self.usuario_aprovacao,
            'data_aprovacao': self.data_aprovacao.isoformat() if self.data_aprovacao else None,
            'sincronizado_sigx': self.sincronizado_sigx,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'tipo_evento': self.tipo_evento.to_dict() if self.tipo_evento else None,
            'veiculo': self.veiculo.to_dict() if self.veiculo else None,
            'motorista': self.motorista.to_dict() if self.motorista else None
        }
    
    def calcular_duracao(self):
        """Calcula a duração do evento em minutos"""
        if self.data_inicio and self.data_fim:
            delta = self.data_fim - self.data_inicio
            self.duracao_minutos = int(delta.total_seconds() / 60)
        return self.duracao_minutos
    
    def aprovar(self, usuario):
        """Aprova o evento para sincronização"""
        self.aprovado = True
        self.usuario_aprovacao = usuario
        self.data_aprovacao = datetime.utcnow()
    
    def __repr__(self):
        return f'<EventoJornada {self.id} - {self.tipo_evento.nome if self.tipo_evento else "N/A"}>'

