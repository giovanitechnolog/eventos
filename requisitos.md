# Sistema de Automatização de Lançamentos de Jornada - SIGx

## Análise de Requisitos

### Objetivo
Desenvolver um sistema que automatize os lançamentos de jornada de trabalho no SIGx através da importação de posições do rastreador e classificação automática/manual de eventos.

### Requisitos Funcionais

#### 1. Importação de Posições do Rastreador
- Importar dados de posição GPS dos veículos
- Processar coordenadas, velocidade, data/hora
- Identificar períodos de movimento e parada
- Calcular distâncias percorridas

#### 2. Classificação Automática de Eventos
- **Interjornada**: Períodos longos parados (>11 horas)
- **Almoço/Refeição**: Paradas de 30-90 minutos em horários específicos
- **Café/Lanche**: Paradas de 15-30 minutos
- **Carga/Descarga**: Paradas em locais específicos com duração variável
- **Abastecimento**: Integração com sistema de abastecimento
- **Check List**: Integração com sistema de check list
- **Manutenção**: Integração com sistema de manutenção

#### 3. Interface de Classificação Manual
- Visualização das posições importadas
- Ferramenta para classificar eventos manualmente
- Edição e correção de classificações automáticas
- Aprovação final dos lançamentos

#### 4. Integração com Sistemas Externos
- API para importar dados de abastecimento
- API para importar dados de check list
- API para importar dados de manutenção
- Sincronização com SIGx

### Estrutura do Banco de Dados

#### Tabela: veiculos
```sql
CREATE TABLE veiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa VARCHAR(10) NOT NULL UNIQUE,
    identificador VARCHAR(20),
    motorista_id INTEGER,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: motoristas
```sql
CREATE TABLE motoristas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    matricula VARCHAR(20),
    funcao VARCHAR(50),
    admissao DATE,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: posicoes_rastreador
```sql
CREATE TABLE posicoes_rastreador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    veiculo_id INTEGER NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    velocidade INTEGER DEFAULT 0,
    endereco TEXT,
    ponto_referencia VARCHAR(200),
    km_aproximado INTEGER,
    tempo_parado INTEGER DEFAULT 0,
    tipo_mensagem VARCHAR(50),
    modo_emergencia BOOLEAN DEFAULT FALSE,
    bateria INTEGER,
    processado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
);
```

#### Tabela: tipos_evento
```sql
CREATE TABLE tipos_evento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao TEXT,
    cor_hex VARCHAR(7),
    duracao_minima INTEGER,
    duracao_maxima INTEGER,
    automatico BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: eventos_jornada
```sql
CREATE TABLE eventos_jornada (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    veiculo_id INTEGER NOT NULL,
    motorista_id INTEGER NOT NULL,
    tipo_evento_id INTEGER NOT NULL,
    data_inicio TIMESTAMP NOT NULL,
    data_fim TIMESTAMP,
    duracao_minutos INTEGER,
    latitude_inicio DECIMAL(10, 8),
    longitude_inicio DECIMAL(11, 8),
    latitude_fim DECIMAL(10, 8),
    longitude_fim DECIMAL(11, 8),
    endereco_inicio TEXT,
    endereco_fim TEXT,
    observacoes TEXT,
    classificacao_automatica BOOLEAN DEFAULT FALSE,
    aprovado BOOLEAN DEFAULT FALSE,
    usuario_aprovacao VARCHAR(50),
    data_aprovacao TIMESTAMP,
    sincronizado_sigx BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
    FOREIGN KEY (motorista_id) REFERENCES motoristas(id),
    FOREIGN KEY (tipo_evento_id) REFERENCES tipos_evento(id)
);
```

#### Tabela: integracao_abastecimento
```sql
CREATE TABLE integracao_abastecimento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    veiculo_id INTEGER NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    posto VARCHAR(100),
    endereco TEXT,
    litros DECIMAL(8, 2),
    valor DECIMAL(10, 2),
    evento_jornada_id INTEGER,
    processado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
    FOREIGN KEY (evento_jornada_id) REFERENCES eventos_jornada(id)
);
```

#### Tabela: integracao_checklist
```sql
CREATE TABLE integracao_checklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    veiculo_id INTEGER NOT NULL,
    motorista_id INTEGER NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    tipo_checklist VARCHAR(50),
    status VARCHAR(20),
    observacoes TEXT,
    evento_jornada_id INTEGER,
    processado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
    FOREIGN KEY (motorista_id) REFERENCES motoristas(id),
    FOREIGN KEY (evento_jornada_id) REFERENCES eventos_jornada(id)
);
```

#### Tabela: integracao_manutencao
```sql
CREATE TABLE integracao_manutencao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    veiculo_id INTEGER NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    tipo_manutencao VARCHAR(50),
    descricao TEXT,
    oficina VARCHAR(100),
    endereco TEXT,
    evento_jornada_id INTEGER,
    processado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
    FOREIGN KEY (evento_jornada_id) REFERENCES eventos_jornada(id)
);
```

### Algoritmos de Classificação Automática

#### 1. Detecção de Interjornada
- Período parado >= 11 horas
- Velocidade = 0 km/h
- Mesmo local (variação < 100 metros)

#### 2. Detecção de Refeições
- Paradas entre 30-90 minutos
- Horários: 11:00-14:00 (almoço) ou 18:00-20:00 (jantar)
- Próximo a restaurantes/pontos de alimentação

#### 3. Detecção de Lanches
- Paradas entre 15-30 minutos
- Qualquer horário
- Próximo a postos/lanchonetes

#### 4. Detecção de Carga/Descarga
- Paradas em locais específicos (empresas/indústrias)
- Duração variável (30 minutos a 4 horas)
- Cruzamento com base de clientes

#### 5. Integração com Sistemas Externos
- Abastecimento: Correlação por data/hora/local
- Check List: Correlação por veículo/motorista/data
- Manutenção: Correlação por veículo/data/oficina

### Arquitetura do Sistema

#### Backend (Python/Flask)
- API REST para importação de dados
- Processamento de posições
- Algoritmos de classificação
- Interface de administração

#### Frontend (HTML/CSS/JavaScript)
- Dashboard de monitoramento
- Interface de classificação manual
- Relatórios e visualizações

#### Banco de Dados (SQLite/PostgreSQL)
- Armazenamento de dados
- Índices para performance
- Backup e recuperação

### Fluxo de Processamento

1. **Importação**: Dados do rastreador são importados via API
2. **Processamento**: Algoritmos analisam as posições
3. **Classificação**: Eventos são classificados automaticamente
4. **Revisão**: Usuário revisa e ajusta classificações
5. **Aprovação**: Eventos são aprovados para sincronização
6. **Sincronização**: Dados são enviados para o SIGx
7. **Monitoramento**: Dashboard mostra status e estatísticas

