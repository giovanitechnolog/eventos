from src.models import db
from datetime import datetime

class TipoEvento(db.Model):
    __tablename__ = 'tipos_evento'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    cor_hex = db.Column(db.String(7))  # Ex: #FF5733
    duracao_minima = db.Column(db.Integer)  # em minutos
    duracao_maxima = db.Column(db.Integer)  # em minutos
    automatico = db.Column(db.Boolean, default=False)  # Se pode ser classificado automaticamente
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'cor_hex': self.cor_hex,
            'duracao_minima': self.duracao_minima,
            'duracao_maxima': self.duracao_maxima,
            'automatico': self.automatico,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def criar_tipos_padrao():
        """Cria os tipos de evento padrão do sistema"""
        tipos_padrao = [
            {
                'nome': 'Interjornada',
                'descricao': 'Período de descanso entre jornadas (mínimo 11 horas)',
                'cor_hex': '#2E86AB',
                'duracao_minima': 660,  # 11 horas
                'duracao_maxima': None,
                'automatico': True
            },
            {
                'nome': 'Almoço',
                'descricao': 'Parada para refeição principal',
                'cor_hex': '#A23B72',
                'duracao_minima': 30,
                'duracao_maxima': 120,
                'automatico': True
            },
            {
                'nome': 'Café/Lanche',
                'descricao': 'Parada para lanche ou café',
                'cor_hex': '#F18F01',
                'duracao_minima': 15,
                'duracao_maxima': 45,
                'automatico': True
            },
            {
                'nome': 'Carga',
                'descricao': 'Operação de carregamento do veículo',
                'cor_hex': '#C73E1D',
                'duracao_minima': 30,
                'duracao_maxima': 240,
                'automatico': False
            },
            {
                'nome': 'Descarga',
                'descricao': 'Operação de descarregamento do veículo',
                'cor_hex': '#C73E1D',
                'duracao_minima': 30,
                'duracao_maxima': 240,
                'automatico': False
            },
            {
                'nome': 'Abastecimento',
                'descricao': 'Abastecimento de combustível',
                'cor_hex': '#3E92CC',
                'duracao_minima': 10,
                'duracao_maxima': 30,
                'automatico': True
            },
            {
                'nome': 'Check List',
                'descricao': 'Verificação de segurança do veículo',
                'cor_hex': '#52B788',
                'duracao_minima': 15,
                'duracao_maxima': 45,
                'automatico': True
            },
            {
                'nome': 'Manutenção',
                'descricao': 'Serviços de manutenção do veículo',
                'cor_hex': '#8E44AD',
                'duracao_minima': 60,
                'duracao_maxima': 480,
                'automatico': True
            },
            {
                'nome': 'Condução',
                'descricao': 'Período de condução do veículo',
                'cor_hex': '#27AE60',
                'duracao_minima': 1,
                'duracao_maxima': None,
                'automatico': True
            },
            {
                'nome': 'Outros',
                'descricao': 'Outros tipos de eventos não categorizados',
                'cor_hex': '#95A5A6',
                'duracao_minima': 1,
                'duracao_maxima': None,
                'automatico': False
            }
        ]
        
        return tipos_padrao
    
    def __repr__(self):
        return f'<TipoEvento {self.nome}>'

