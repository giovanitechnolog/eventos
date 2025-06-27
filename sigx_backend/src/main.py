import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models import db, inicializar_dados_padrao
from src.routes.posicoes import posicoes_bp
from src.routes.eventos import eventos_bp
from src.routes.veiculos import veiculos_bp
from src.routes.motoristas import motoristas_bp
from src.routes.integracoes import integracoes_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'sigx_automation_2025'

# Habilitar CORS para todas as rotas
CORS(app)

# Registrar blueprints
app.register_blueprint(posicoes_bp, url_prefix='/api/posicoes')
app.register_blueprint(eventos_bp, url_prefix='/api/eventos')
app.register_blueprint(veiculos_bp, url_prefix='/api/veiculos')
app.register_blueprint(motoristas_bp, url_prefix='/api/motoristas')
app.register_blueprint(integracoes_bp, url_prefix='/api/integracoes')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar tabelas e dados padrão
with app.app_context():
    db.create_all()
    inicializar_dados_padrao()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "Sistema SIGx - Automatização de Jornadas", 200

@app.route('/api/status')
def status():
    return {
        'status': 'online',
        'sistema': 'SIGx Automatização de Jornadas',
        'versao': '1.0.0',
        'modulos': {
            'posicoes': 'Importação e processamento de posições GPS',
            'eventos': 'Gestão e classificação de eventos de jornada',
            'veiculos': 'Cadastro e gestão de veículos',
            'motoristas': 'Cadastro e gestão de motoristas',
            'integracoes': 'Integração com sistemas externos (abastecimento, checklist, manutenção)'
        }
    }

@app.route('/api/documentacao')
def documentacao():
    return {
        'titulo': 'SIGx - Sistema de Automatização de Jornadas',
        'versao': '1.0.0',
        'descricao': 'API para automatização de lançamentos de jornada de trabalho',
        'endpoints': {
            'posicoes': {
                'POST /api/posicoes/importar': 'Importa posições do rastreador',
                'GET /api/posicoes/veiculo/{id}': 'Lista posições de um veículo',
                'POST /api/posicoes/classificar/{id}': 'Classifica posições automaticamente',
                'GET /api/posicoes/estatisticas/{id}': 'Estatísticas de posições',
                'GET /api/posicoes/exemplo-importacao': 'Exemplo de formato de importação'
            },
            'eventos': {
                'POST /api/eventos/criar': 'Cria novo evento',
                'GET /api/eventos/listar': 'Lista eventos com filtros',
                'GET /api/eventos/{id}': 'Obtém evento específico',
                'PUT /api/eventos/{id}/atualizar': 'Atualiza evento',
                'POST /api/eventos/{id}/aprovar': 'Aprova evento',
                'DELETE /api/eventos/{id}/excluir': 'Exclui evento',
                'GET /api/eventos/tipos': 'Lista tipos de evento',
                'GET /api/eventos/estatisticas': 'Estatísticas de eventos'
            },
            'veiculos': {
                'GET /api/veiculos/listar': 'Lista veículos',
                'POST /api/veiculos/criar': 'Cria novo veículo',
                'GET /api/veiculos/{id}': 'Obtém veículo específico',
                'PUT /api/veiculos/{id}/atualizar': 'Atualiza veículo'
            },
            'motoristas': {
                'GET /api/motoristas/listar': 'Lista motoristas',
                'POST /api/motoristas/criar': 'Cria novo motorista',
                'GET /api/motoristas/{id}': 'Obtém motorista específico',
                'PUT /api/motoristas/{id}/atualizar': 'Atualiza motorista'
            },
            'integracoes': {
                'POST /api/integracoes/abastecimento/importar': 'Importa dados de abastecimento',
                'POST /api/integracoes/abastecimento/processar': 'Processa abastecimentos',
                'GET /api/integracoes/abastecimento/listar': 'Lista abastecimentos',
                'POST /api/integracoes/checklist/importar': 'Importa dados de checklist',
                'POST /api/integracoes/checklist/processar': 'Processa checklists',
                'GET /api/integracoes/checklist/listar': 'Lista checklists',
                'POST /api/integracoes/manutencao/importar': 'Importa dados de manutenção',
                'POST /api/integracoes/manutencao/processar': 'Processa manutenções',
                'GET /api/integracoes/manutencao/listar': 'Lista manutenções',
                'GET /api/integracoes/estatisticas': 'Estatísticas de integrações'
            }
        },
        'fluxo_trabalho': [
            '1. Importar posições do rastreador via /api/posicoes/importar',
            '2. Classificar eventos automaticamente via /api/posicoes/classificar/{veiculo_id}',
            '3. Revisar e editar eventos via interface web ou API',
            '4. Aprovar eventos via /api/eventos/{id}/aprovar',
            '5. Importar dados externos (abastecimento, checklist, manutenção)',
            '6. Sincronizar com SIGx (funcionalidade futura)'
        ]
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

