from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models import db, Motorista

motoristas_bp = Blueprint('motoristas', __name__)

@motoristas_bp.route('/listar', methods=['GET'])
def listar_motoristas():
    """Lista todos os motoristas"""
    try:
        ativo = request.args.get('ativo')
        
        query = Motorista.query
        
        if ativo is not None:
            ativo = ativo.lower() == 'true'
            query = query.filter(Motorista.ativo == ativo)
        
        motoristas = query.order_by(Motorista.nome).all()
        
        return jsonify({
            'motoristas': [motorista.to_dict() for motorista in motoristas],
            'total': len(motoristas)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@motoristas_bp.route('/criar', methods=['POST'])
def criar_motorista():
    """Cria um novo motorista"""
    try:
        data = request.get_json()
        
        if not data or 'nome' not in data:
            return jsonify({'erro': 'Nome é obrigatório'}), 400
        
        # Verificar se CPF já existe (se fornecido)
        if data.get('cpf'):
            motorista_existente = Motorista.query.filter_by(cpf=data['cpf']).first()
            if motorista_existente:
                return jsonify({'erro': 'Motorista com este CPF já existe'}), 400
        
        # Converter data de admissão se fornecida
        admissao = None
        if data.get('admissao'):
            admissao = datetime.fromisoformat(data['admissao']).date()
        
        motorista = Motorista(
            nome=data['nome'],
            cpf=data.get('cpf'),
            matricula=data.get('matricula'),
            funcao=data.get('funcao'),
            admissao=admissao,
            ativo=data.get('ativo', True)
        )
        
        db.session.add(motorista)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'motorista': motorista.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@motoristas_bp.route('/<int:motorista_id>', methods=['GET'])
def obter_motorista(motorista_id):
    """Obtém detalhes de um motorista específico"""
    try:
        motorista = Motorista.query.get(motorista_id)
        if not motorista:
            return jsonify({'erro': 'Motorista não encontrado'}), 404
        
        return jsonify(motorista.to_dict())
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@motoristas_bp.route('/<int:motorista_id>/atualizar', methods=['PUT'])
def atualizar_motorista(motorista_id):
    """Atualiza um motorista existente"""
    try:
        motorista = Motorista.query.get(motorista_id)
        if not motorista:
            return jsonify({'erro': 'Motorista não encontrado'}), 404
        
        data = request.get_json()
        
        # Verificar se novo CPF já existe (se foi alterado)
        if 'cpf' in data and data['cpf'] and data['cpf'] != motorista.cpf:
            motorista_existente = Motorista.query.filter_by(cpf=data['cpf']).first()
            if motorista_existente:
                return jsonify({'erro': 'Motorista com este CPF já existe'}), 400
        
        # Atualizar campos
        campos_atualizaveis = ['nome', 'cpf', 'matricula', 'funcao', 'ativo']
        for campo in campos_atualizaveis:
            if campo in data:
                setattr(motorista, campo, data[campo])
        
        # Tratar data de admissão separadamente
        if 'admissao' in data and data['admissao']:
            motorista.admissao = datetime.fromisoformat(data['admissao']).date()
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'motorista': motorista.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

