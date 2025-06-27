from flask_sqlalchemy import SQLAlchemy

# Instância única do SQLAlchemy
db = SQLAlchemy()

# Importar todos os modelos
from src.models.veiculo import Veiculo
from src.models.motorista import Motorista
from src.models.posicao_rastreador import PosicaoRastreador
from src.models.tipo_evento import TipoEvento
from src.models.evento_jornada import EventoJornada
from src.models.integracoes import IntegracaoAbastecimento, IntegracaoChecklist, IntegracaoManutencao

# Função para inicializar dados padrão
def inicializar_dados_padrao():
    """Inicializa dados padrão no banco de dados"""
    
    # Verificar se já existem tipos de evento
    if TipoEvento.query.count() == 0:
        tipos_padrao = TipoEvento.criar_tipos_padrao()
        
        for tipo_data in tipos_padrao:
            tipo = TipoEvento(**tipo_data)
            db.session.add(tipo)
        
        db.session.commit()
        print("Tipos de evento padrão criados com sucesso!")
    
    # Criar motorista e veículo de exemplo se não existirem
    if Motorista.query.count() == 0:
        from datetime import date
        
        motorista_exemplo = Motorista(
            nome="Sidney Viana Fonseca",
            cpf="051.984.056-98",
            matricula="5149",
            funcao="Motorista de Carreta",
            admissao=date(2013, 4, 10)
        )
        db.session.add(motorista_exemplo)
        db.session.commit()
        
        veiculo_exemplo = Veiculo(
            placa="QXT1F69",
            identificador="L - F1187",
            motorista_id=motorista_exemplo.id
        )
        db.session.add(veiculo_exemplo)
        db.session.commit()
        
        print("Dados de exemplo criados com sucesso!")

# Exportar todos os modelos
__all__ = [
    'db',
    'Veiculo',
    'Motorista', 
    'PosicaoRastreador',
    'TipoEvento',
    'EventoJornada',
    'IntegracaoAbastecimento',
    'IntegracaoChecklist',
    'IntegracaoManutencao',
    'inicializar_dados_padrao'
]

