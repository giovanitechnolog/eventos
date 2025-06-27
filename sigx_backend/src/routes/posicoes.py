from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models import db, PosicaoRastreador, Veiculo
from src.classificador_eventos import classificar_eventos_automaticamente, AnalisadorPadroes
import json

posicoes_bp = Blueprint('posicoes', __name__)

@posicoes_bp.route('/importar', methods=['POST'])
def importar_posicoes():
    """
    Importa posições do rastreador
    Formato esperado:
    {
        "veiculo_placa": "QXT1F69",
        "posicoes": [
            {
                "data_hora": "2025-06-21T11:56:00",
                "latitude": -20.3911,
                "longitude": -45.5418,
                "velocidade": 0,
                "endereco": "MG - TIMÓTEO - Próx. Avenida Waldomiro Duarte",
                "ponto_referencia": "Aperam Inox America Do Sul S.a",
                "km_aproximado": 0,
                "tempo_parado": 0,
                "tipo_mensagem": "Posição Normal",
                "modo_emergencia": false,
                "bateria": 29
            }
        ],
        "classificar_automaticamente": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'veiculo_placa' not in data or 'posicoes' not in data:
            return jsonify({'erro': 'Dados inválidos. Necessário veiculo_placa e posicoes'}), 400
        
        # Buscar veículo
        veiculo = Veiculo.query.filter_by(placa=data['veiculo_placa']).first()
        if not veiculo:
            return jsonify({'erro': f'Veículo com placa {data["veiculo_placa"]} não encontrado'}), 404
        
        posicoes_importadas = 0
        posicoes_duplicadas = 0
        
        for posicao_data in data['posicoes']:
            try:
                # Converter string de data para datetime
                data_hora = datetime.fromisoformat(posicao_data['data_hora'].replace('Z', '+00:00'))
                
                # Verificar se a posição já existe
                posicao_existente = PosicaoRastreador.query.filter_by(
                    veiculo_id=veiculo.id,
                    data_hora=data_hora
                ).first()
                
                if posicao_existente:
                    posicoes_duplicadas += 1
                    continue
                
                # Criar nova posição
                nova_posicao = PosicaoRastreador(
                    veiculo_id=veiculo.id,
                    data_hora=data_hora,
                    latitude=posicao_data.get('latitude'),
                    longitude=posicao_data.get('longitude'),
                    velocidade=posicao_data.get('velocidade', 0),
                    endereco=posicao_data.get('endereco'),
                    ponto_referencia=posicao_data.get('ponto_referencia'),
                    km_aproximado=posicao_data.get('km_aproximado'),
                    tempo_parado=posicao_data.get('tempo_parado', 0),
                    tipo_mensagem=posicao_data.get('tipo_mensagem'),
                    modo_emergencia=posicao_data.get('modo_emergencia', False),
                    bateria=posicao_data.get('bateria')
                )
                
                db.session.add(nova_posicao)
                posicoes_importadas += 1
                
            except Exception as e:
                print(f"Erro ao processar posição: {e}")
                continue
        
        db.session.commit()
        
        resultado = {
            'sucesso': True,
            'posicoes_importadas': posicoes_importadas,
            'posicoes_duplicadas': posicoes_duplicadas,
            'veiculo': veiculo.to_dict()
        }
        
        # Classificar automaticamente se solicitado
        if data.get('classificar_automaticamente', False) and posicoes_importadas > 0:
            try:
                eventos_classificados = classificar_eventos_automaticamente(veiculo.id)
                resultado['eventos_classificados'] = len(eventos_classificados)
                resultado['eventos'] = eventos_classificados
            except Exception as e:
                resultado['erro_classificacao'] = f"Erro na classificação automática: {str(e)}"
        
        return jsonify(resultado)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@posicoes_bp.route('/veiculo/<int:veiculo_id>', methods=['GET'])
def listar_posicoes_veiculo(veiculo_id):
    """Lista posições de um veículo específico"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        processado = request.args.get('processado')
        limite = request.args.get('limite', type=int, default=1000)
        
        query = PosicaoRastreador.query.filter_by(veiculo_id=veiculo_id)
        
        # Filtros opcionais
        if data_inicio:
            data_inicio = datetime.fromisoformat(data_inicio)
            query = query.filter(PosicaoRastreador.data_hora >= data_inicio)
        
        if data_fim:
            data_fim = datetime.fromisoformat(data_fim)
            query = query.filter(PosicaoRastreador.data_hora <= data_fim)
        
        if processado is not None:
            processado = processado.lower() == 'true'
            query = query.filter(PosicaoRastreador.processado == processado)
        
        posicoes = query.order_by(PosicaoRastreador.data_hora.desc()).limit(limite).all()
        
        return jsonify({
            'posicoes': [posicao.to_dict() for posicao in posicoes],
            'total': len(posicoes)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@posicoes_bp.route('/classificar/<int:veiculo_id>', methods=['POST'])
def classificar_posicoes(veiculo_id):
    """Classifica posições não processadas de um veículo usando IA"""
    try:
        data = request.get_json() or {}
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        
        # Converter datas se fornecidas
        if data_inicio:
            data_inicio = datetime.fromisoformat(data_inicio)
        if data_fim:
            data_fim = datetime.fromisoformat(data_fim)
        
        # Executar classificação automática
        eventos_classificados = classificar_eventos_automaticamente(
            veiculo_id, data_inicio, data_fim
        )
        
        return jsonify({
            'sucesso': True,
            'eventos_classificados': len(eventos_classificados),
            'eventos': eventos_classificados
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@posicoes_bp.route('/analisar-padroes/<int:motorista_id>', methods=['GET'])
def analisar_padroes_motorista(motorista_id):
    """Analisa padrões históricos de um motorista"""
    try:
        dias = request.args.get('dias', type=int, default=30)
        
        padroes = AnalisadorPadroes.analisar_historico_motorista(motorista_id, dias)
        
        return jsonify({
            'motorista_id': motorista_id,
            'periodo_dias': dias,
            'padroes': padroes
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@posicoes_bp.route('/sugestoes-melhoria/<int:veiculo_id>', methods=['GET'])
def sugestoes_melhoria_classificacao(veiculo_id):
    """Sugere melhorias na classificação baseado em padrões"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if data_inicio:
            data_inicio = datetime.fromisoformat(data_inicio)
        if data_fim:
            data_fim = datetime.fromisoformat(data_fim)
        
        sugestoes = AnalisadorPadroes.sugerir_melhorias_classificacao(
            veiculo_id, data_inicio, data_fim
        )
        
        return jsonify({
            'veiculo_id': veiculo_id,
            'sugestoes': sugestoes,
            'total_sugestoes': len(sugestoes)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@posicoes_bp.route('/estatisticas/<int:veiculo_id>', methods=['GET'])
def estatisticas_posicoes(veiculo_id):
    """Retorna estatísticas das posições de um veículo"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = PosicaoRastreador.query.filter_by(veiculo_id=veiculo_id)
        
        if data_inicio:
            data_inicio = datetime.fromisoformat(data_inicio)
            query = query.filter(PosicaoRastreador.data_hora >= data_inicio)
        
        if data_fim:
            data_fim = datetime.fromisoformat(data_fim)
            query = query.filter(PosicaoRastreador.data_hora <= data_fim)
        
        posicoes = query.order_by(PosicaoRastreador.data_hora).all()
        
        if not posicoes:
            return jsonify({'erro': 'Nenhuma posição encontrada'}), 404
        
        # Calcular estatísticas
        total_posicoes = len(posicoes)
        posicoes_processadas = sum(1 for p in posicoes if p.processado)
        posicoes_parado = sum(1 for p in posicoes if p.velocidade <= 5)
        posicoes_movimento = total_posicoes - posicoes_parado
        
        # Calcular distância total (aproximada)
        distancia_total = 0
        tempo_movimento = 0
        tempo_parado = 0
        
        for i in range(1, len(posicoes)):
            # Distância
            if posicoes[i].latitude and posicoes[i].longitude and posicoes[i-1].latitude and posicoes[i-1].longitude:
                distancia = PosicaoRastreador.calcular_distancia(
                    posicoes[i-1].latitude, posicoes[i-1].longitude,
                    posicoes[i].latitude, posicoes[i].longitude
                )
                distancia_total += distancia
            
            # Tempo
            delta_tempo = (posicoes[i].data_hora - posicoes[i-1].data_hora).total_seconds() / 60
            if posicoes[i].velocidade > 5:
                tempo_movimento += delta_tempo
            else:
                tempo_parado += delta_tempo
        
        # Velocidade média (apenas em movimento)
        velocidade_media = 0
        if tempo_movimento > 0:
            velocidade_media = (distancia_total / 1000) / (tempo_movimento / 60)
        
        return jsonify({
            'veiculo_id': veiculo_id,
            'periodo': {
                'inicio': posicoes[0].data_hora.isoformat(),
                'fim': posicoes[-1].data_hora.isoformat(),
                'duracao_horas': round((posicoes[-1].data_hora - posicoes[0].data_hora).total_seconds() / 3600, 2)
            },
            'estatisticas': {
                'total_posicoes': total_posicoes,
                'posicoes_processadas': posicoes_processadas,
                'posicoes_pendentes': total_posicoes - posicoes_processadas,
                'posicoes_parado': posicoes_parado,
                'posicoes_movimento': posicoes_movimento,
                'distancia_total_km': round(distancia_total / 1000, 2),
                'tempo_movimento_horas': round(tempo_movimento / 60, 2),
                'tempo_parado_horas': round(tempo_parado / 60, 2),
                'velocidade_media_kmh': round(velocidade_media, 2),
                'percentual_parado': round((posicoes_parado / total_posicoes) * 100, 2),
                'percentual_movimento': round((posicoes_movimento / total_posicoes) * 100, 2)
            }
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@posicoes_bp.route('/exemplo-importacao', methods=['GET'])
def exemplo_importacao():
    """Retorna um exemplo de formato para importação de posições"""
    exemplo = {
        "veiculo_placa": "QXT1F69",
        "classificar_automaticamente": True,
        "posicoes": [
            {
                "data_hora": "2025-06-21T11:56:00",
                "latitude": -20.3911,
                "longitude": -45.5418,
                "velocidade": 0,
                "endereco": "MG - TIMÓTEO - Próx. Avenida Waldomiro Duarte",
                "ponto_referencia": "Aperam Inox America Do Sul S.a",
                "km_aproximado": 0,
                "tempo_parado": 0,
                "tipo_mensagem": "Posição Normal",
                "modo_emergencia": False,
                "bateria": 29
            },
            {
                "data_hora": "2025-06-21T15:10:00",
                "latitude": -20.3915,
                "longitude": -45.5420,
                "velocidade": 45,
                "endereco": "MG - TIMÓTEO - BR-381",
                "ponto_referencia": "Rodovia BR-381",
                "km_aproximado": 5,
                "tempo_parado": 0,
                "tipo_mensagem": "Posição Normal",
                "modo_emergencia": False,
                "bateria": 28
            }
        ]
    }
    
    return jsonify({
        'exemplo': exemplo,
        'instrucoes': {
            'veiculo_placa': 'Placa do veículo (obrigatório)',
            'classificar_automaticamente': 'Se deve classificar eventos automaticamente (opcional, padrão: false)',
            'posicoes': 'Array de posições do rastreador',
            'data_hora': 'Data e hora no formato ISO 8601',
            'latitude/longitude': 'Coordenadas GPS em decimal',
            'velocidade': 'Velocidade em km/h',
            'endereco': 'Endereço ou localização textual',
            'ponto_referencia': 'Ponto de referência próximo',
            'outros_campos': 'Campos opcionais para informações adicionais'
        }
    })

