from src.models import db
from datetime import datetime

class PosicaoRastreador(db.Model):
    __tablename__ = 'posicoes_rastreador'
    
    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    velocidade = db.Column(db.Integer, default=0)
    endereco = db.Column(db.Text)
    ponto_referencia = db.Column(db.String(200))
    km_aproximado = db.Column(db.Integer)
    tempo_parado = db.Column(db.Integer, default=0)  # em minutos
    tipo_mensagem = db.Column(db.String(50))
    modo_emergencia = db.Column(db.Boolean, default=False)
    bateria = db.Column(db.Integer)
    processado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'veiculo_id': self.veiculo_id,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'velocidade': self.velocidade,
            'endereco': self.endereco,
            'ponto_referencia': self.ponto_referencia,
            'km_aproximado': self.km_aproximado,
            'tempo_parado': self.tempo_parado,
            'tipo_mensagem': self.tipo_mensagem,
            'modo_emergencia': self.modo_emergencia,
            'bateria': self.bateria,
            'processado': self.processado,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def calcular_distancia(lat1, lon1, lat2, lon2):
        """Calcula a distância entre duas coordenadas em metros usando a fórmula de Haversine"""
        import math
        
        if not all([lat1, lon1, lat2, lon2]):
            return 0
            
        # Converter graus para radianos
        lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        
        # Fórmula de Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Raio da Terra em metros
        r = 6371000
        
        return c * r
    
    def __repr__(self):
        return f'<PosicaoRastreador {self.veiculo_id} - {self.data_hora}>'

