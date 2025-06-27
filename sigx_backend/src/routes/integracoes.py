from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models import db, IntegracaoAbastecimento, IntegracaoChecklist, IntegracaoManutencao, EventoJornada, TipoEvento, Veiculo

integracoes_bp = Blueprint('integracoes', __name__)

# ==================== ABASTECIMENTO ====================

@integracoes_bp.route('/abastecimento/importar', methods=['POST'])
def importar_abastecimento():
    """
    Importa dados de abastecimento
    Formato esperado:
    {
        "abastecimentos": [
            {
                "veiculo_placa": "QXT1F69",
                "data_hora": "2025-06-21T14:30:00",
                "posto": "Posto Shell BR-381",
                "endereco": "BR-381, Km 445, Timóteo/MG",
                "litros": 150.5,
                "valor": 850.75
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'abastecimentos' not in data:
            return jsonify({'erro': 'Dados inválidos. Necessário array de abastecimentos'}), 400
        
        abastecimentos_importados = 0
        abastecimentos_duplicados = 0
        eventos_correlacionados = 0
        
        for abast_data in data['abastecimentos']:
            try:
                # Buscar veículo
                veiculo = Veiculo.query.filter_by(placa=abast_data['veiculo_placa']).first()
                if not veiculo:
                    continue
                
                # Converter data
                data_hora = datetime.fromisoformat(abast_data['data_hora'])
                
                # Verificar duplicata
                existente = IntegracaoAbastecimento.query.filter_by(
                    veiculo_id=veiculo.id,
                    data_hora=data_hora
                ).first()
                
                if existente:
                    abastecimentos_duplicados += 1
                    continue
                
                # Criar registro
                abastecimento = IntegracaoAbastecimento(
                    veiculo_id=veiculo.id,
                    data_hora=data_hora,
                    posto=abast_data.get('posto'),
                    endereco=abast_data.get('endereco'),
                    litros=abast_data.get('litros'),
                    valor=abast_data.get('valor')
                )
                
                db.session.add(abastecimento)
                abastecimentos_importados += 1
                
                # Tentar correlacionar com evento existente
                evento_correlacionado = _correlacionar_abastecimento(abastecimento)
                if evento_correlacionado:
                    eventos_correlacionados += 1
                
            except Exception as e:
                print(f"Erro ao processar abastecimento: {e}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'abastecimentos_importados': abastecimentos_importados,
            'abastecimentos_duplicados': abastecimentos_duplicados,
            'eventos_correlacionados': eventos_correlacionados
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@integracoes_bp.route('/abastecimento/processar', methods=['POST'])
def processar_abastecimentos():
    """Processa abastecimentos não processados e cria eventos automaticamente"""
    try:
        # Buscar abastecimentos não processados
        abastecimentos = IntegracaoAbastecimento.query.filter_by(processado=False).all()
        
        eventos_criados = 0
        
        for abastecimento in abastecimentos:
            # Verificar se já existe evento correlacionado
            if abastecimento.evento_jornada_id:
                abastecimento.processado = True
                continue
            
            # Buscar tipo de evento "Abastecimento"
            tipo_abastecimento = TipoEvento.query.filter_by(nome='Abastecimento').first()
            if not tipo_abastecimento:
                continue
            
            # Buscar veículo e motorista
            veiculo = abastecimento.veiculo
            if not veiculo or not veiculo.motorista_id:
                continue
            
            # Criar evento de abastecimento
            evento = EventoJornada(
                veiculo_id=veiculo.id,
                motorista_id=veiculo.motorista_id,
                tipo_evento_id=tipo_abastecimento.id,
                data_inicio=abastecimento.data_hora,
                data_fim=abastecimento.data_hora + timedelta(minutes=20),  # Duração estimada
                duracao_minutos=20,
                endereco_inicio=abastecimento.endereco,
                endereco_fim=abastecimento.endereco,
                observacoes=f"Abastecimento automático - {abastecimento.posto} - {abastecimento.litros}L",
                classificacao_automatica=True
            )
            
            db.session.add(evento)
            db.session.flush()  # Para obter o ID
            
            # Associar abastecimento ao evento
            abastecimento.evento_jornada_id = evento.id
            abastecimento.processado = True
            
            eventos_criados += 1
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'eventos_criados': eventos_criados,
            'abastecimentos_processados': len(abastecimentos)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

# ==================== CHECK LIST ====================

@integracoes_bp.route('/checklist/importar', methods=['POST'])
def importar_checklist():
    """
    Importa dados de check list
    Formato esperado:
    {
        "checklists": [
            {
                "veiculo_placa": "QXT1F69",
                "motorista_cpf": "051.984.056-98",
                "data_hora": "2025-06-21T06:00:00",
                "tipo_checklist": "saida",
                "status": "aprovado",
                "observacoes": "Veículo em perfeitas condições"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'checklists' not in data:
            return jsonify({'erro': 'Dados inválidos. Necessário array de checklists'}), 400
        
        checklists_importados = 0
        checklists_duplicados = 0
        eventos_correlacionados = 0
        
        for check_data in data['checklists']:
            try:
                # Buscar veículo
                veiculo = Veiculo.query.filter_by(placa=check_data['veiculo_placa']).first()
                if not veiculo:
                    continue
                
                # Buscar motorista por CPF
                from src.models import Motorista
                motorista = Motorista.query.filter_by(cpf=check_data['motorista_cpf']).first()
                if not motorista:
                    continue
                
                # Converter data
                data_hora = datetime.fromisoformat(check_data['data_hora'])
                
                # Verificar duplicata
                existente = IntegracaoChecklist.query.filter_by(
                    veiculo_id=veiculo.id,
                    motorista_id=motorista.id,
                    data_hora=data_hora,
                    tipo_checklist=check_data['tipo_checklist']
                ).first()
                
                if existente:
                    checklists_duplicados += 1
                    continue
                
                # Criar registro
                checklist = IntegracaoChecklist(
                    veiculo_id=veiculo.id,
                    motorista_id=motorista.id,
                    data_hora=data_hora,
                    tipo_checklist=check_data.get('tipo_checklist'),
                    status=check_data.get('status'),
                    observacoes=check_data.get('observacoes')
                )
                
                db.session.add(checklist)
                checklists_importados += 1
                
                # Tentar correlacionar com evento existente
                evento_correlacionado = _correlacionar_checklist(checklist)
                if evento_correlacionado:
                    eventos_correlacionados += 1
                
            except Exception as e:
                print(f"Erro ao processar checklist: {e}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'checklists_importados': checklists_importados,
            'checklists_duplicados': checklists_duplicados,
            'eventos_correlacionados': eventos_correlacionados
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@integracoes_bp.route('/checklist/processar', methods=['POST'])
def processar_checklists():
    """Processa checklists não processados e cria eventos automaticamente"""
    try:
        # Buscar checklists não processados
        checklists = IntegracaoChecklist.query.filter_by(processado=False).all()
        
        eventos_criados = 0
        
        for checklist in checklists:
            # Verificar se já existe evento correlacionado
            if checklist.evento_jornada_id:
                checklist.processado = True
                continue
            
            # Buscar tipo de evento "Check List"
            tipo_checklist = TipoEvento.query.filter_by(nome='Check List').first()
            if not tipo_checklist:
                continue
            
            # Criar evento de checklist
            evento = EventoJornada(
                veiculo_id=checklist.veiculo_id,
                motorista_id=checklist.motorista_id,
                tipo_evento_id=tipo_checklist.id,
                data_inicio=checklist.data_hora,
                data_fim=checklist.data_hora + timedelta(minutes=15),  # Duração estimada
                duracao_minutos=15,
                observacoes=f"Check List {checklist.tipo_checklist} - Status: {checklist.status}",
                classificacao_automatica=True
            )
            
            db.session.add(evento)
            db.session.flush()  # Para obter o ID
            
            # Associar checklist ao evento
            checklist.evento_jornada_id = evento.id
            checklist.processado = True
            
            eventos_criados += 1
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'eventos_criados': eventos_criados,
            'checklists_processados': len(checklists)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

# ==================== MANUTENÇÃO ====================

@integracoes_bp.route('/manutencao/importar', methods=['POST'])
def importar_manutencao():
    """
    Importa dados de manutenção
    Formato esperado:
    {
        "manutencoes": [
            {
                "veiculo_placa": "QXT1F69",
                "data_hora": "2025-06-21T08:00:00",
                "tipo_manutencao": "preventiva",
                "descricao": "Troca de óleo e filtros",
                "oficina": "Oficina Central Ltda",
                "endereco": "Rua das Oficinas, 123, Timóteo/MG"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'manutencoes' not in data:
            return jsonify({'erro': 'Dados inválidos. Necessário array de manutenções'}), 400
        
        manutencoes_importadas = 0
        manutencoes_duplicadas = 0
        eventos_correlacionados = 0
        
        for manut_data in data['manutencoes']:
            try:
                # Buscar veículo
                veiculo = Veiculo.query.filter_by(placa=manut_data['veiculo_placa']).first()
                if not veiculo:
                    continue
                
                # Converter data
                data_hora = datetime.fromisoformat(manut_data['data_hora'])
                
                # Verificar duplicata
                existente = IntegracaoManutencao.query.filter_by(
                    veiculo_id=veiculo.id,
                    data_hora=data_hora,
                    tipo_manutencao=manut_data['tipo_manutencao']
                ).first()
                
                if existente:
                    manutencoes_duplicadas += 1
                    continue
                
                # Criar registro
                manutencao = IntegracaoManutencao(
                    veiculo_id=veiculo.id,
                    data_hora=data_hora,
                    tipo_manutencao=manut_data.get('tipo_manutencao'),
                    descricao=manut_data.get('descricao'),
                    oficina=manut_data.get('oficina'),
                    endereco=manut_data.get('endereco')
                )
                
                db.session.add(manutencao)
                manutencoes_importadas += 1
                
                # Tentar correlacionar com evento existente
                evento_correlacionado = _correlacionar_manutencao(manutencao)
                if evento_correlacionado:
                    eventos_correlacionados += 1
                
            except Exception as e:
                print(f"Erro ao processar manutenção: {e}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'manutencoes_importadas': manutencoes_importadas,
            'manutencoes_duplicadas': manutencoes_duplicadas,
            'eventos_correlacionados': eventos_correlacionados
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@integracoes_bp.route('/manutencao/processar', methods=['POST'])
def processar_manutencoes():
    """Processa manutenções não processadas e cria eventos automaticamente"""
    try:
        # Buscar manutenções não processadas
        manutencoes = IntegracaoManutencao.query.filter_by(processado=False).all()
        
        eventos_criados = 0
        
        for manutencao in manutencoes:
            # Verificar se já existe evento correlacionado
            if manutencao.evento_jornada_id:
                manutencao.processado = True
                continue
            
            # Buscar tipo de evento "Manutenção"
            tipo_manutencao = TipoEvento.query.filter_by(nome='Manutenção').first()
            if not tipo_manutencao:
                continue
            
            # Buscar veículo e motorista
            veiculo = manutencao.veiculo
            if not veiculo or not veiculo.motorista_id:
                continue
            
            # Estimar duração baseada no tipo
            duracao = 120  # 2 horas padrão
            if manutencao.tipo_manutencao == 'preventiva':
                duracao = 180  # 3 horas
            elif manutencao.tipo_manutencao == 'corretiva':
                duracao = 240  # 4 horas
            
            # Criar evento de manutenção
            evento = EventoJornada(
                veiculo_id=veiculo.id,
                motorista_id=veiculo.motorista_id,
                tipo_evento_id=tipo_manutencao.id,
                data_inicio=manutencao.data_hora,
                data_fim=manutencao.data_hora + timedelta(minutes=duracao),
                duracao_minutos=duracao,
                endereco_inicio=manutencao.endereco,
                endereco_fim=manutencao.endereco,
                observacoes=f"Manutenção {manutencao.tipo_manutencao} - {manutencao.oficina} - {manutencao.descricao}",
                classificacao_automatica=True
            )
            
            db.session.add(evento)
            db.session.flush()  # Para obter o ID
            
            # Associar manutenção ao evento
            manutencao.evento_jornada_id = evento.id
            manutencao.processado = True
            
            eventos_criados += 1
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'eventos_criados': eventos_criados,
            'manutencoes_processadas': len(manutencoes)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

# ==================== FUNÇÕES AUXILIARES ====================

def _correlacionar_abastecimento(abastecimento):
    """Tenta correlacionar abastecimento com evento existente"""
    # Buscar eventos de abastecimento próximos (±30 minutos)
    inicio = abastecimento.data_hora - timedelta(minutes=30)
    fim = abastecimento.data_hora + timedelta(minutes=30)
    
    tipo_abastecimento = TipoEvento.query.filter_by(nome='Abastecimento').first()
    if not tipo_abastecimento:
        return False
    
    evento = EventoJornada.query.filter(
        EventoJornada.veiculo_id == abastecimento.veiculo_id,
        EventoJornada.tipo_evento_id == tipo_abastecimento.id,
        EventoJornada.data_inicio >= inicio,
        EventoJornada.data_inicio <= fim
    ).first()
    
    if evento:
        abastecimento.evento_jornada_id = evento.id
        # Atualizar observações do evento
        if evento.observacoes:
            evento.observacoes += f" | Dados: {abastecimento.litros}L - R$ {abastecimento.valor}"
        else:
            evento.observacoes = f"Abastecimento: {abastecimento.litros}L - R$ {abastecimento.valor}"
        return True
    
    return False

def _correlacionar_checklist(checklist):
    """Tenta correlacionar checklist com evento existente"""
    # Buscar eventos de checklist próximos (±15 minutos)
    inicio = checklist.data_hora - timedelta(minutes=15)
    fim = checklist.data_hora + timedelta(minutes=15)
    
    tipo_checklist = TipoEvento.query.filter_by(nome='Check List').first()
    if not tipo_checklist:
        return False
    
    evento = EventoJornada.query.filter(
        EventoJornada.veiculo_id == checklist.veiculo_id,
        EventoJornada.motorista_id == checklist.motorista_id,
        EventoJornada.tipo_evento_id == tipo_checklist.id,
        EventoJornada.data_inicio >= inicio,
        EventoJornada.data_inicio <= fim
    ).first()
    
    if evento:
        checklist.evento_jornada_id = evento.id
        # Atualizar observações do evento
        if evento.observacoes:
            evento.observacoes += f" | Status: {checklist.status}"
        else:
            evento.observacoes = f"Check List {checklist.tipo_checklist} - Status: {checklist.status}"
        return True
    
    return False

def _correlacionar_manutencao(manutencao):
    """Tenta correlacionar manutenção com evento existente"""
    # Buscar eventos de manutenção próximos (±60 minutos)
    inicio = manutencao.data_hora - timedelta(minutes=60)
    fim = manutencao.data_hora + timedelta(minutes=60)
    
    tipo_manutencao = TipoEvento.query.filter_by(nome='Manutenção').first()
    if not tipo_manutencao:
        return False
    
    evento = EventoJornada.query.filter(
        EventoJornada.veiculo_id == manutencao.veiculo_id,
        EventoJornada.tipo_evento_id == tipo_manutencao.id,
        EventoJornada.data_inicio >= inicio,
        EventoJornada.data_inicio <= fim
    ).first()
    
    if evento:
        manutencao.evento_jornada_id = evento.id
        # Atualizar observações do evento
        if evento.observacoes:
            evento.observacoes += f" | {manutencao.oficina}: {manutencao.descricao}"
        else:
            evento.observacoes = f"Manutenção em {manutencao.oficina}: {manutencao.descricao}"
        return True
    
    return False

# ==================== ROTAS DE CONSULTA ====================

@integracoes_bp.route('/abastecimento/listar', methods=['GET'])
def listar_abastecimentos():
    """Lista abastecimentos com filtros"""
    try:
        veiculo_id = request.args.get('veiculo_id', type=int)
        processado = request.args.get('processado')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = IntegracaoAbastecimento.query
        
        if veiculo_id:
            query = query.filter(IntegracaoAbastecimento.veiculo_id == veiculo_id)
        
        if processado is not None:
            processado = processado.lower() == 'true'
            query = query.filter(IntegracaoAbastecimento.processado == processado)
        
        if data_inicio:
            data_inicio = datetime.fromisoformat(data_inicio)
            query = query.filter(IntegracaoAbastecimento.data_hora >= data_inicio)
        
        if data_fim:
            data_fim = datetime.fromisoformat(data_fim)
            query = query.filter(IntegracaoAbastecimento.data_hora <= data_fim)
        
        abastecimentos = query.order_by(IntegracaoAbastecimento.data_hora.desc()).all()
        
        return jsonify({
            'abastecimentos': [abast.to_dict() for abast in abastecimentos],
            'total': len(abastecimentos)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@integracoes_bp.route('/checklist/listar', methods=['GET'])
def listar_checklists():
    """Lista checklists com filtros"""
    try:
        veiculo_id = request.args.get('veiculo_id', type=int)
        motorista_id = request.args.get('motorista_id', type=int)
        processado = request.args.get('processado')
        
        query = IntegracaoChecklist.query
        
        if veiculo_id:
            query = query.filter(IntegracaoChecklist.veiculo_id == veiculo_id)
        
        if motorista_id:
            query = query.filter(IntegracaoChecklist.motorista_id == motorista_id)
        
        if processado is not None:
            processado = processado.lower() == 'true'
            query = query.filter(IntegracaoChecklist.processado == processado)
        
        checklists = query.order_by(IntegracaoChecklist.data_hora.desc()).all()
        
        return jsonify({
            'checklists': [check.to_dict() for check in checklists],
            'total': len(checklists)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@integracoes_bp.route('/manutencao/listar', methods=['GET'])
def listar_manutencoes():
    """Lista manutenções com filtros"""
    try:
        veiculo_id = request.args.get('veiculo_id', type=int)
        processado = request.args.get('processado')
        tipo = request.args.get('tipo')
        
        query = IntegracaoManutencao.query
        
        if veiculo_id:
            query = query.filter(IntegracaoManutencao.veiculo_id == veiculo_id)
        
        if processado is not None:
            processado = processado.lower() == 'true'
            query = query.filter(IntegracaoManutencao.processado == processado)
        
        if tipo:
            query = query.filter(IntegracaoManutencao.tipo_manutencao == tipo)
        
        manutencoes = query.order_by(IntegracaoManutencao.data_hora.desc()).all()
        
        return jsonify({
            'manutencoes': [manut.to_dict() for manut in manutencoes],
            'total': len(manutencoes)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@integracoes_bp.route('/estatisticas', methods=['GET'])
def estatisticas_integracoes():
    """Retorna estatísticas das integrações"""
    try:
        veiculo_id = request.args.get('veiculo_id', type=int)
        
        # Filtros base
        abast_query = IntegracaoAbastecimento.query
        check_query = IntegracaoChecklist.query
        manut_query = IntegracaoManutencao.query
        
        if veiculo_id:
            abast_query = abast_query.filter(IntegracaoAbastecimento.veiculo_id == veiculo_id)
            check_query = check_query.filter(IntegracaoChecklist.veiculo_id == veiculo_id)
            manut_query = manut_query.filter(IntegracaoManutencao.veiculo_id == veiculo_id)
        
        # Contar registros
        total_abastecimentos = abast_query.count()
        abast_processados = abast_query.filter(IntegracaoAbastecimento.processado == True).count()
        
        total_checklists = check_query.count()
        check_processados = check_query.filter(IntegracaoChecklist.processado == True).count()
        
        total_manutencoes = manut_query.count()
        manut_processadas = manut_query.filter(IntegracaoManutencao.processado == True).count()
        
        return jsonify({
            'abastecimento': {
                'total': total_abastecimentos,
                'processados': abast_processados,
                'pendentes': total_abastecimentos - abast_processados
            },
            'checklist': {
                'total': total_checklists,
                'processados': check_processados,
                'pendentes': total_checklists - check_processados
            },
            'manutencao': {
                'total': total_manutencoes,
                'processados': manut_processadas,
                'pendentes': total_manutencoes - manut_processadas
            }
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

