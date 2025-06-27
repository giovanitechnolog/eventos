# 🚀 Instalação Rápida - Sistema SIGx

## Início Rápido (5 minutos)

### 1. Executar o Sistema
```bash
cd sigx_automation
./iniciar_sistema.sh
```

### 2. Acessar Interface
- Abrir navegador em: **http://localhost:5001**
- Se a porta estiver ocupada, o sistema usará automaticamente a 5002

### 3. Testar Importação
1. Na interface web, ir para aba "Importar"
2. Selecionar o arquivo `exemplo_posicoes.json`
3. Marcar "Classificar automaticamente"
4. Clicar "Importar Posições"

### 4. Verificar Resultados
- Ir para aba "Dashboard" para ver estatísticas
- Ir para aba "Eventos" para revisar classificações
- Aprovar eventos conforme necessário

## Estrutura do Projeto

```
sigx_automation/
├── README.md                 # Documentação completa
├── iniciar_sistema.sh        # Script de inicialização
├── exemplo_posicoes.json     # Dados de teste
├── test_sistema.py          # Script de testes
├── requisitos.md            # Análise de requisitos
└── sigx_backend/            # Aplicação principal
    ├── src/
    │   ├── main.py          # Servidor Flask
    │   ├── models/          # Modelos do banco
    │   ├── routes/          # APIs REST
    │   ├── static/          # Interface web
    │   └── classificador_eventos.py
    ├── venv/                # Ambiente virtual
    └── requirements.txt     # Dependências
```

## Funcionalidades Principais

### ✅ Implementado
- [x] Importação de posições GPS
- [x] Classificação automática de eventos
- [x] Interface web completa
- [x] Gestão de veículos e motoristas
- [x] Aprovação de eventos
- [x] Integração com sistemas externos
- [x] APIs REST completas
- [x] Dashboard com estatísticas

### 🔄 Tipos de Evento Suportados
- **Interjornada** - Descanso obrigatório (11h+)
- **Almoço** - Refeições (30-90 min)
- **Café** - Pausas curtas (10-30 min)
- **Carga/Descarga** - Operações (30-240 min)
- **Abastecimento** - Combustível (10-30 min)
- **Check List** - Verificações (10-20 min)
- **Manutenção** - Serviços (60-480 min)

### 📊 Algoritmo de Classificação
O sistema usa IA para classificar eventos baseado em:
- Duração da parada
- Horário do dia
- Localização (endereço/ponto de referência)
- Padrões históricos do motorista
- Contexto da jornada

## Integração com SIGx

### Dados de Entrada
- **Posições GPS**: Arquivo JSON do rastreador
- **Abastecimento**: Dados do sistema de combustível
- **Check List**: Dados do sistema de verificações
- **Manutenção**: Dados do sistema de oficina

### Dados de Saída
- **Eventos Classificados**: Prontos para o SIGx
- **Relatórios**: Conformidade de jornada
- **Estatísticas**: Dashboard gerencial

## Suporte

### Problemas Comuns
1. **Porta em uso**: O script mudará automaticamente para 5002
2. **Erro de dependências**: Execute `pip install -r requirements.txt`
3. **Arquivo não encontrado**: Verifique se está no diretório correto

### Logs
- Logs do servidor: `sigx_backend/server.log`
- Logs da interface: Console do navegador (F12)

### Contato
Para suporte técnico ou dúvidas sobre implementação, consulte a documentação completa no arquivo `README.md`.

---

**Sistema desenvolvido para automatizar 100% dos lançamentos de jornada, eliminando trabalho manual e garantindo conformidade regulatória.**

