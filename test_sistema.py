#!/usr/bin/env python3
"""
Script de teste para o Sistema SIGx de Automatização de Jornadas
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001"

def test_api_status():
    """Testa se a API está online"""
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Status: Online")
            print(f"   Sistema: {data.get('sistema')}")
            print(f"   Versão: {data.get('versao')}")
            return True
        else:
            print("❌ API Status: Erro")
            return False
    except Exception as e:
        print(f"❌ API Status: Erro de conexão - {e}")
        return False

def test_veiculos():
    """Testa API de veículos"""
    try:
        response = requests.get(f"{BASE_URL}/api/veiculos/listar", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Veículos: Funcionando")
            print(f"   Total de veículos: {len(data.get('veiculos', []))}")
            return True
        else:
            print(f"❌ API Veículos: Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Veículos: Erro - {e}")
        return False

def test_motoristas():
    """Testa API de motoristas"""
    try:
        response = requests.get(f"{BASE_URL}/api/motoristas/listar", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Motoristas: Funcionando")
            print(f"   Total de motoristas: {len(data.get('motoristas', []))}")
            return True
        else:
            print(f"❌ API Motoristas: Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Motoristas: Erro - {e}")
        return False

def test_eventos():
    """Testa API de eventos"""
    try:
        response = requests.get(f"{BASE_URL}/api/eventos/listar", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Eventos: Funcionando")
            print(f"   Total de eventos: {len(data.get('eventos', []))}")
            return True
        else:
            print(f"❌ API Eventos: Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Eventos: Erro - {e}")
        return False

def test_tipos_evento():
    """Testa API de tipos de evento"""
    try:
        response = requests.get(f"{BASE_URL}/api/eventos/tipos", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Tipos de Evento: Funcionando")
            print(f"   Total de tipos: {len(data.get('tipos_evento', []))}")
            return True
        else:
            print(f"❌ API Tipos de Evento: Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Tipos de Evento: Erro - {e}")
        return False

def test_exemplo_importacao():
    """Testa API de exemplo de importação"""
    try:
        response = requests.get(f"{BASE_URL}/api/posicoes/exemplo-importacao", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Exemplo Importação: Funcionando")
            print(f"   Exemplo disponível: {'exemplo' in data}")
            return True
        else:
            print(f"❌ API Exemplo Importação: Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Exemplo Importação: Erro - {e}")
        return False

def test_integracoes():
    """Testa APIs de integração"""
    try:
        response = requests.get(f"{BASE_URL}/api/integracoes/estatisticas", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Integrações: Funcionando")
            print(f"   Módulos disponíveis: abastecimento, checklist, manutenção")
            return True
        else:
            print(f"❌ API Integrações: Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Integrações: Erro - {e}")
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do Sistema SIGx")
    print("=" * 50)
    
    tests = [
        test_api_status,
        test_veiculos,
        test_motoristas,
        test_eventos,
        test_tipos_evento,
        test_exemplo_importacao,
        test_integracoes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Resultado dos Testes: {passed}/{total} passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

