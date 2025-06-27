from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models import db, EventoJornada, TipoEvento, Veiculo, Motorista

eventos_bp = Blueprint('eventos', __name__)

@eventos_bp.route('/criar', methods=['POST'])
def criar_evento():
    """
    Cria um novo evento de jornada
    Formato esperado:
    {
        "veiculo_id": 1,
        "motorista_id": 1,
        "tipo_evento_id": 1,
        "data_inicio": "2025-06-21T11:56:00",
        "data_fim": "2025-06-21T15:10:00",
        "latitude_inicio": -20.3911,
        "longitude_inicio": -45.5418,
        "latitude_fim": -20.3911,
        "longitude_fim": -45.5418,
        "endereco_inicio": "Timóteo/MG",
        "endereco_fim": "Timóteo/MG",
        "observacoes": "Descarga na Aperam",
        "classificacao_automatica": true
    }
    """
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        campos_obrigatorios = ['veiculo_id', 'motorista_id', 'tipo_evento_id', 'data_inicio']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({'erro': f'Campo obrigatório: {campo}'}), 400
        
        # Verificar se veículo, motorista e tipo de evento existem
        veiculo = Veiculo.query.get(data['veiculo_id'])
        if not veiculo:
            return jsonify({'erro': 'Veículo não encontrado'}), 404
        
        motorista = Motorista.query.get(data['motorista_id'])
        if not motorista:
            return jsonify({'erro': 'Motorista não encontrado'}), 404
        
        tipo_evento = TipoEvento.query.get(data['tipo_evento_id'])
        if not tipo_evento:
            return jsonify({'erro': 'Tipo de evento não encontrado'}), 404
        
        # Converter datas
        data_inicio = datetime.fromisoformat(data['data_inicio'])
        data_fim = None
        if data.get('data_fim'):
            data_fim = datetime.fromisoformat(data['data_fim'])
        
        # Criar evento
        evento = EventoJornada(
            veiculo_id=data['veiculo_id'],
            motorista_id=data['motorista_id'],
            tipo_evento_id=data['tipo_evento_id'],
            data_inicio=data_inicio,
            data_fim=data_fim,
            latitude_inicio=data.get('latitude_inicio'),
            longitude_inicio=data.get('longitude_inicio'),
            latitude_fim=data.get('latitude_fim'),
            longitude_fim=data.get('longitude_fim'),
            endereco_inicio=data.get('endereco_inicio'),
            endereco_fim=data.get('endereco_fim'),
            observacoes=data.get('observacoes'),
            classificacao_automatica=data.get('classificacao_automatica', False)
        )
        
        # Calcular duração se data_fim estiver presente
        if data_fim:
            evento.calcular_duracao()
        
        db.session.add(evento)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'evento': evento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@eventos_bp.route('/listar', methods=['GET'])
def listar_eventos():
    """Lista eventos com filtros opcionais"""
    try:
        # Parâmetros de filtro
        veiculo_id = request.args.get('veiculo_id', type=int)
        motorista_id = request.args.get('motorista_id', type=int)
        tipo_evento_id = request.args.get('tipo_evento_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        aprovado = request.args.get('aprovado')
        classificacao_automatica = request.args.get('classificacao_automatica')
        
        query = EventoJornada.query
        
        # Aplicar filtros
        if veiculo_id:
            query = query.filter(EventoJornada.veiculo_id == veiculo_id)
        
        if motorista_id:
            query = query.filter(EventoJornada.motorista_id == motorista_id)
        
        if tipo_evento_id:
            query = query.filter(EventoJornada.tipo_evento_id == tipo_evento_id)
        
        if data_inicio:
            data_inicio = datetime.fromisoformat(data_inicio)
            query = query.filter(EventoJornada.data_inicio >= data_inicio)
        
        if data_fim:
            data_fim = datetime.fromisoformat(data_fim)
            query = query.filter(EventoJornada.data_inicio <= data_fim)
        
        if aprovado is not None:
            aprovado = aprovado.lower() == 'true'
            query = query.filter(EventoJornada.aprovado == aprovado)
        
        if classificacao_automatica is not None:
            classificacao_automatica = classificacao_automatica.lower() == 'true'
            query = query.filter(EventoJornada.classificacao_automatica == classificacao_automatica)
        
        eventos = query.order_by(EventoJornada.data_inicio.desc()).all()
        
        return jsonify({
            'eventos': [evento.to_dict() for evento in eventos],
            'total': len(eventos)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@eventos_bp.route('/<int:evento_id>', methods=['GET'])
def obter_evento(evento_id):
    """Obtém detalhes de um evento específico"""
    try:
        evento = EventoJornada.query.get(evento_id)
        if not evento:
            return jsonify({'erro': 'Evento não encontrado'}), 404
        
        return jsonify(evento.to_dict())
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@eventos_bp.route('/<int:evento_id>/atualizar', methods=['PUT'])
def atualizar_evento(evento_id):
    """Atualiza um evento existente"""
    try:
        evento = EventoJornada.query.get(evento_id)
        if not evento:
            return jsonify({'erro': 'Evento não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        campos_atualizaveis = [
            'tipo_evento_id', 'data_inicio', 'data_fim', 'latitude_inicio',
            'longitude_inicio', 'latitude_fim', 'longitude_fim',
            'endereco_inicio', 'endereco_fim', 'observacoes'
        ]
        
        for campo in campos_atualizaveis:
            if campo in data:
                if campo in ['data_inicio', 'data_fim'] and data[campo]:
                    setattr(evento, campo, datetime.fromisoformat(data[campo]))
                else:
                    setattr(evento, campo, data[campo])
        
        # Recalcular duração se necessário
        if evento.data_fim:
            evento.calcular_duracao()
        
        # Marcar como não aprovado se foi modificado
        if not evento.classificacao_automatica:
            evento.aprovado = False
            evento.usuario_aprovacao = None
            evento.data_aprovacao = None
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'evento': evento.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@eventos_bp.route('/<int:evento_id>/aprovar', methods=['POST'])
def aprovar_evento(evento_id):
    """Aprova um evento para sincronização com o SIGx"""
    try:
        evento = EventoJornada.query.get(evento_id)
        if not evento:
            return jsonify({'erro': 'Evento não encontrado'}), 404
        
        data = request.get_json() or {}
        usuario = data.get('usuario', 'Sistema')
        
        evento.aprovar(usuario)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'evento': evento.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@eventos_bp.route('/<int:evento_id>/reprovar', methods=['POST'])
def reprovar_evento(evento_id):
    """Remove aprovação de um evento"""
    try:
        evento = EventoJornada.query.get(evento_id)
        if not evento:
            return jsonify({'erro': 'Evento não encontrado'}), 404
        
        evento.aprovado = False
        evento.usuario_aprovacao = None
        evento.data_aprovacao = None
        evento.sincronizado_sigx = False
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'evento': evento.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@eventos_bp.route('/<int:evento_id>/excluir', methods=['DELETE'])
def excluir_evento(evento_id):
    """Exclui um evento"""
    try:
        evento = EventoJornada.query.get(evento_id)
        if not evento:
            return jsonify({'erro': 'Evento não encontrado'}), 404
        
        # Não permitir exclusão de eventos já sincronizados
        if evento.sincronizado_sigx:
            return jsonify({'erro': 'Não é possível excluir evento já sincronizado com o SIGx'}), 400
        
        db.session.delete(evento)
        db.session.commit()
        
        return jsonify({'sucesso': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@eventos_bp.route('/tipos', methods=['GET'])
def listar_tipos_evento():
    """Lista todos os tipos de evento disponíveis"""
    try:
        tipos = TipoEvento.query.filter_by(ativo=True).order_by(TipoEvento.nome).all()
        
        return jsonify({
            'tipos_evento': [tipo.to_dict() for tipo in tipos],
            'total': len(tipos)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@eventos_bp.route('/estatisticas', methods=['GET'])
def estatisticas_eventos():
    """Retorna estatísticas dos eventos"""
    try:
        veiculo_id = request.args.get('veiculo_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = EventoJornada.query
        
        if veiculo_id:
            query = query.filter(EventoJornada.veiculo_id == veiculo_id)
        
        if data_inicio:
            data_inicio = datetime.fromisoformat(data_inicio)
            query = query.filter(EventoJornada.data_inicio >= data_inicio)
        
        if data_fim:
            data_fim = datetime.fromisoformat(data_fim)
            query = query.filter(EventoJornada.data_inicio <= data_fim)
        
        eventos = query.all()
        
        # Calcular estatísticas
        total_eventos = len(eventos)
        eventos_aprovados = sum(1 for e in eventos if e.aprovado)
        eventos_automaticos = sum(1 for e in eventos if e.classificacao_automatica)
        eventos_sincronizados = sum(1 for e in eventos if e.sincronizado_sigx)
        
        # Estatísticas por tipo
        tipos_stats = {}
        for evento in eventos:
            tipo_nome = evento.tipo_evento.nome if evento.tipo_evento else 'Desconhecido'
            if tipo_nome not in tipos_stats:
                tipos_stats[tipo_nome] = 0
            tipos_stats[tipo_nome] += 1
        
        return jsonify({
            'estatisticas': {
                'total_eventos': total_eventos,
                'eventos_aprovados': eventos_aprovados,
                'eventos_pendentes': total_eventos - eventos_aprovados,
                'eventos_automaticos': eventos_automaticos,
                'eventos_manuais': total_eventos - eventos_automaticos,
                'eventos_sincronizados': eventos_sincronizados,
                'percentual_aprovados': round((eventos_aprovados / total_eventos) * 100, 2) if total_eventos > 0 else 0,
                'percentual_automaticos': round((eventos_automaticos / total_eventos) * 100, 2) if total_eventos > 0 else 0
            },
            'por_tipo': tipos_stats
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

