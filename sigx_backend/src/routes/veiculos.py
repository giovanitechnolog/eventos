from flask import Blueprint, request, jsonify
from src.models import db, Veiculo, Motorista

veiculos_bp = Blueprint('veiculos', __name__)

@veiculos_bp.route('/listar', methods=['GET'])
def listar_veiculos():
    """Lista todos os veículos"""
    try:
        ativo = request.args.get('ativo')
        
        query = Veiculo.query
        
        if ativo is not None:
            ativo = ativo.lower() == 'true'
            query = query.filter(Veiculo.ativo == ativo)
        
        veiculos = query.order_by(Veiculo.placa).all()
        
        return jsonify({
            'veiculos': [veiculo.to_dict() for veiculo in veiculos],
            'total': len(veiculos)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@veiculos_bp.route('/criar', methods=['POST'])
def criar_veiculo():
    """Cria um novo veículo"""
    try:
        data = request.get_json()
        
        if not data or 'placa' not in data:
            return jsonify({'erro': 'Placa é obrigatória'}), 400
        
        # Verificar se placa já existe
        veiculo_existente = Veiculo.query.filter_by(placa=data['placa']).first()
        if veiculo_existente:
            return jsonify({'erro': 'Veículo com esta placa já existe'}), 400
        
        veiculo = Veiculo(
            placa=data['placa'],
            identificador=data.get('identificador'),
            motorista_id=data.get('motorista_id'),
            ativo=data.get('ativo', True)
        )
        
        db.session.add(veiculo)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'veiculo': veiculo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@veiculos_bp.route('/<int:veiculo_id>', methods=['GET'])
def obter_veiculo(veiculo_id):
    """Obtém detalhes de um veículo específico"""
    try:
        veiculo = Veiculo.query.get(veiculo_id)
        if not veiculo:
            return jsonify({'erro': 'Veículo não encontrado'}), 404
        
        return jsonify(veiculo.to_dict())
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@veiculos_bp.route('/<int:veiculo_id>/atualizar', methods=['PUT'])
def atualizar_veiculo(veiculo_id):
    """Atualiza um veículo existente"""
    try:
        veiculo = Veiculo.query.get(veiculo_id)
        if not veiculo:
            return jsonify({'erro': 'Veículo não encontrado'}), 404
        
        data = request.get_json()
        
        # Verificar se nova placa já existe (se foi alterada)
        if 'placa' in data and data['placa'] != veiculo.placa:
            veiculo_existente = Veiculo.query.filter_by(placa=data['placa']).first()
            if veiculo_existente:
                return jsonify({'erro': 'Veículo com esta placa já existe'}), 400
        
        # Atualizar campos
        campos_atualizaveis = ['placa', 'identificador', 'motorista_id', 'ativo']
        for campo in campos_atualizaveis:
            if campo in data:
                setattr(veiculo, campo, data[campo])
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'veiculo': veiculo.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

