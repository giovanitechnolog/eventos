#!/bin/bash

# Script de Inicialização do Sistema SIGx
# Automatização de Jornadas de Trabalho

echo "🚀 Iniciando Sistema SIGx - Automatização de Jornadas"
echo "=================================================="

# Verificar se estamos no diretório correto
if [ ! -d "sigx_backend" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    exit 1
fi

# Navegar para o diretório do backend
cd sigx_backend

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Erro: Ambiente virtual não encontrado"
    echo "   Execute: python -m venv venv"
    exit 1
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Verificar dependências
echo "📦 Verificando dependências..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erro: Arquivo requirements.txt não encontrado"
    exit 1
fi

# Instalar dependências se necessário
pip install -q -r requirements.txt

# Verificar se o banco de dados existe
if [ ! -f "src/database/app.db" ]; then
    echo "🗄️  Criando banco de dados..."
    mkdir -p src/database
fi

# Verificar porta disponível
PORT=5001
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Porta $PORT está em uso. Tentando porta 5002..."
    PORT=5002
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Erro: Portas 5001 e 5002 estão em uso"
        echo "   Pare outros serviços ou use uma porta diferente"
        exit 1
    fi
fi

# Atualizar porta no arquivo main.py se necessário
if [ $PORT -ne 5001 ]; then
    sed -i "s/port=5001/port=$PORT/g" src/main.py
fi

echo "🌐 Iniciando servidor na porta $PORT..."
echo "   Acesse: http://localhost:$PORT"
echo ""
echo "📋 Para parar o servidor, pressione Ctrl+C"
echo "=================================================="

# Iniciar servidor
python src/main.py

