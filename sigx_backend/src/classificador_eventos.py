"""
Módulo de Classificação Automática de Eventos
Sistema inteligente para identificar e classificar eventos de jornada automaticamente
"""

from datetime import datetime, timedelta
from src.models import db, PosicaoRastreador, EventoJornada, TipoEvento, Veiculo, Motorista
import re

class ClassificadorEventos:
    """Classe principal para classificação automática de eventos"""
    
    def __init__(self):
        self.tipos_evento = {}
        self._carregar_tipos_evento()
    
    def _carregar_tipos_evento(self):
        """Carrega os tipos de evento do banco de dados"""
        tipos = TipoEvento.query.filter_by(ativo=True).all()
        for tipo in tipos:
            self.tipos_evento[tipo.nome] = tipo
    
    def processar_veiculo(self, veiculo_id, data_inicio=None, data_fim=None):
        """
        Processa todas as posições de um veículo e identifica eventos automaticamente
        """
        # Buscar posições não processadas
        query = PosicaoRastreador.query.filter_by(
            veiculo_id=veiculo_id,
            processado=False
        ).order_by(PosicaoRastreador.data_hora)
        
        if data_inicio:
            query = query.filter(PosicaoRastreador.data_hora >= data_inicio)
        if data_fim:
            query = query.filter(PosicaoRastreador.data_hora <= data_fim)
        
        posicoes = query.all()
        
        if not posicoes:
            return []
        
        # Buscar informações do veículo e motorista
        veiculo = Veiculo.query.get(veiculo_id)
        if not veiculo or not veiculo.motorista_id:
            raise ValueError("Veículo não encontrado ou sem motorista associado")
        
        # Identificar períodos de parada e movimento
        periodos = self._identificar_periodos(posicoes)
        
        # Classificar cada período
        eventos_identificados = []
        for periodo in periodos:
            evento = self._classificar_periodo(periodo, veiculo.id, veiculo.motorista_id)
            if evento:
                eventos_identificados.append(evento)
        
        # Marcar posições como processadas
        for posicao in posicoes:
            posicao.processado = True
        
        db.session.commit()
        
        return eventos_identificados
    
    def _identificar_periodos(self, posicoes):
        """Identifica períodos de parada e movimento"""
        periodos = []
        periodo_atual = None
        
        for i, posicao in enumerate(posicoes):
            # Determinar se está parado ou em movimento
            em_movimento = posicao.velocidade > 5  # Considera movimento acima de 5 km/h
            
            if periodo_atual is None:
                # Primeiro período
                periodo_atual = {
                    'tipo': 'movimento' if em_movimento else 'parada',
                    'inicio': posicao,
                    'fim': posicao,
                    'posicoes': [posicao]
                }
            elif (em_movimento and periodo_atual['tipo'] == 'movimento') or \
                 (not em_movimento and periodo_atual['tipo'] == 'parada'):
                # Continuação do período atual
                periodo_atual['fim'] = posicao
                periodo_atual['posicoes'].append(posicao)
            else:
                # Mudança de tipo - finalizar período atual e iniciar novo
                periodos.append(periodo_atual)
                periodo_atual = {
                    'tipo': 'movimento' if em_movimento else 'parada',
                    'inicio': posicao,
                    'fim': posicao,
                    'posicoes': [posicao]
                }
        
        # Adicionar último período
        if periodo_atual:
            periodos.append(periodo_atual)
        
        return periodos
    
    def _classificar_periodo(self, periodo, veiculo_id, motorista_id):
        """Classifica um período específico"""
        duracao_minutos = self._calcular_duracao_minutos(periodo['inicio'].data_hora, periodo['fim'].data_hora)
        
        # Períodos muito curtos (menos de 5 minutos) são ignorados
        if duracao_minutos < 5:
            return None
        
        if periodo['tipo'] == 'parada':
            return self._classificar_parada(periodo, veiculo_id, motorista_id, duracao_minutos)
        else:
            return self._classificar_movimento(periodo, veiculo_id, motorista_id, duracao_minutos)
    
    def _classificar_parada(self, periodo, veiculo_id, motorista_id, duracao_minutos):
        """Classifica uma parada"""
        hora_inicio = periodo['inicio'].data_hora.hour
        ponto_referencia = periodo['inicio'].ponto_referencia or ''
        endereco = periodo['inicio'].endereco or ''
        
        # 1. Interjornada (11+ horas)
        if duracao_minutos >= 660:  # 11 horas
            tipo_evento = self.tipos_evento.get('Interjornada')
            return self._criar_evento(
                veiculo_id, motorista_id, tipo_evento.id, periodo, duracao_minutos,
                observacoes="Interjornada identificada automaticamente"
            )
        
        # 2. Abastecimento (baseado no local)
        if self._e_posto_combustivel(ponto_referencia, endereco) and 10 <= duracao_minutos <= 45:
            tipo_evento = self.tipos_evento.get('Abastecimento')
            return self._criar_evento(
                veiculo_id, motorista_id, tipo_evento.id, periodo, duracao_minutos,
                observacoes=f"Abastecimento em {ponto_referencia or endereco}"
            )
        
        # 3. Carga/Descarga (baseado no local e horário)
        if self._e_local_carga_descarga(ponto_referencia, endereco) and 30 <= duracao_minutos <= 300:
            if hora_inicio < 12:
                tipo_evento = self.tipos_evento.get('Carga')
                observacoes = f"Carga em {ponto_referencia or endereco}"
            else:
                tipo_evento = self.tipos_evento.get('Descarga')
                observacoes = f"Descarga em {ponto_referencia or endereco}"
            
            return self._criar_evento(
                veiculo_id, motorista_id, tipo_evento.id, periodo, duracao_minutos,
                observacoes=observacoes
            )
        
        # 4. Refeições (baseado no horário e duração)
        if 30 <= duracao_minutos <= 120:
            if 11 <= hora_inicio <= 14:  # Horário de almoço
                tipo_evento = self.tipos_evento.get('Almoço')
                return self._criar_evento(
                    veiculo_id, motorista_id, tipo_evento.id, periodo, duracao_minutos,
                    observacoes="Almoço identificado por horário"
                )
            elif 18 <= hora_inicio <= 21:  # Horário de jantar
                tipo_evento = self.tipos_evento.get('Almoço')
                return self._criar_evento(
                    veiculo_id, motorista_id, tipo_evento.id, periodo, duracao_minutos,
                    observacoes="Jantar identificado por horário"
                )
        
        # 5. Lanche/Café
        if 15 <= duracao_minutos <= 45:
            tipo_evento = self.tipos_evento.get('Café/Lanche')
            return self._criar_evento(
                veiculo_id, motorista_id, tipo_evento.id, periodo, duracao_minutos,
                observacoes="Lanche/café identificado por duração"
            )
        
        # 6. Manutenção (baseado no local)
        if self._e_oficina_manutencao(ponto_referencia, endereco) and 60 <= duracao_minutos <= 480:
            tipo_evento = self.tipos_evento.get('Manutenção')
            return self._criar_evento(
                veiculo_id, motorista_id, tipo_evento.id, periodo, duracao_minutos,
                observacoes=f"Manutenção em {ponto_referencia or endereco}"
            )
        
        # 7. Outros (paradas não categorizadas)
        tipo_evento = self.tipos_evento.get('Outros')
        return self._criar_evento(
            veiculo_id, motorista_id, tipo_evento.id, periodo, duracao_minutos,
            observacoes="Parada não categorizada automaticamente"
        )
    
    def _classificar_movimento(self, periodo, veiculo_id, motorista_id, duracao_minutos):
        """Classifica um período de movimento como condução"""
        # Períodos de movimento são classificados como condução
        tipo_evento = self.tipos_evento.get('Condução')
        
        # Calcular distância aproximada
        distancia_km = self._calcular_distancia_periodo(periodo)
        
        return self._criar_evento(
            veiculo_id, motorista_id, tipo_evento.id, periodo, duracao_minutos,
            observacoes=f"Condução - Distância aproximada: {distancia_km:.1f} km"
        )
    
    def _e_posto_combustivel(self, ponto_referencia, endereco):
        """Verifica se o local é um posto de combustível"""
        texto = f"{ponto_referencia} {endereco}".lower()
        palavras_posto = [
            'posto', 'combustivel', 'shell', 'petrobras', 'ipiranga', 'br',
            'ale', 'texaco', 'esso', 'dom pedro', 'gasolina', 'diesel'
        ]
        return any(palavra in texto for palavra in palavras_posto)
    
    def _e_local_carga_descarga(self, ponto_referencia, endereco):
        """Verifica se o local é adequado para carga/descarga"""
        texto = f"{ponto_referencia} {endereco}".lower()
        palavras_carga = [
            'empresa', 'industria', 'fabrica', 'deposito', 'armazem',
            'terminal', 'porto', 'patio', 'usina', 'mineracao',
            'siderurgica', 'metalurgica', 'quimica', 'cimento',
            'aperam', 'csn', 'vale', 'olatrans'
        ]
        return any(palavra in texto for palavra in palavras_carga)
    
    def _e_oficina_manutencao(self, ponto_referencia, endereco):
        """Verifica se o local é uma oficina de manutenção"""
        texto = f"{ponto_referencia} {endereco}".lower()
        palavras_oficina = [
            'oficina', 'manutencao', 'revisao', 'mecanica', 'borracharia',
            'eletrica', 'funilaria', 'pintura', 'lavagem', 'servicos'
        ]
        return any(palavra in texto for palavra in palavras_oficina)
    
    def _calcular_duracao_minutos(self, inicio, fim):
        """Calcula duração em minutos entre duas datas"""
        delta = fim - inicio
        return int(delta.total_seconds() / 60)
    
    def _calcular_distancia_periodo(self, periodo):
        """Calcula distância aproximada percorrida no período"""
        distancia_total = 0
        posicoes = periodo['posicoes']
        
        for i in range(1, len(posicoes)):
            if posicoes[i].latitude and posicoes[i].longitude and \
               posicoes[i-1].latitude and posicoes[i-1].longitude:
                distancia = PosicaoRastreador.calcular_distancia(
                    posicoes[i-1].latitude, posicoes[i-1].longitude,
                    posicoes[i].latitude, posicoes[i].longitude
                )
                distancia_total += distancia
        
        return distancia_total / 1000  # Converter para km
    
    def _criar_evento(self, veiculo_id, motorista_id, tipo_evento_id, periodo, duracao_minutos, observacoes=""):
        """Cria um evento de jornada"""
        evento = EventoJornada(
            veiculo_id=veiculo_id,
            motorista_id=motorista_id,
            tipo_evento_id=tipo_evento_id,
            data_inicio=periodo['inicio'].data_hora,
            data_fim=periodo['fim'].data_hora,
            duracao_minutos=duracao_minutos,
            latitude_inicio=periodo['inicio'].latitude,
            longitude_inicio=periodo['inicio'].longitude,
            latitude_fim=periodo['fim'].latitude,
            longitude_fim=periodo['fim'].longitude,
            endereco_inicio=periodo['inicio'].endereco,
            endereco_fim=periodo['fim'].endereco,
            observacoes=observacoes,
            classificacao_automatica=True
        )
        
        db.session.add(evento)
        db.session.commit()
        
        return evento.to_dict()


class AnalisadorPadroes:
    """Classe para análise de padrões e melhoria da classificação"""
    
    @staticmethod
    def analisar_historico_motorista(motorista_id, dias=30):
        """Analisa padrões históricos de um motorista"""
        data_limite = datetime.now() - timedelta(days=dias)
        
        eventos = EventoJornada.query.filter(
            EventoJornada.motorista_id == motorista_id,
            EventoJornada.data_inicio >= data_limite,
            EventoJornada.aprovado == True
        ).all()
        
        padroes = {
            'horarios_refeicao': [],
            'locais_frequentes': {},
            'duracao_media_eventos': {},
            'total_eventos': len(eventos)
        }
        
        for evento in eventos:
            tipo_nome = evento.tipo_evento.nome if evento.tipo_evento else 'Desconhecido'
            
            # Analisar horários de refeição
            if tipo_nome == 'Almoço':
                padroes['horarios_refeicao'].append(evento.data_inicio.hour)
            
            # Analisar locais frequentes
            if evento.endereco_inicio:
                if evento.endereco_inicio not in padroes['locais_frequentes']:
                    padroes['locais_frequentes'][evento.endereco_inicio] = 0
                padroes['locais_frequentes'][evento.endereco_inicio] += 1
            
            # Analisar duração média por tipo
            if tipo_nome not in padroes['duracao_media_eventos']:
                padroes['duracao_media_eventos'][tipo_nome] = []
            if evento.duracao_minutos:
                padroes['duracao_media_eventos'][tipo_nome].append(evento.duracao_minutos)
        
        # Calcular médias
        for tipo in padroes['duracao_media_eventos']:
            duracoes = padroes['duracao_media_eventos'][tipo]
            padroes['duracao_media_eventos'][tipo] = {
                'media': sum(duracoes) / len(duracoes),
                'minima': min(duracoes),
                'maxima': max(duracoes),
                'total_eventos': len(duracoes)
            }
        
        return padroes
    
    @staticmethod
    def sugerir_melhorias_classificacao(veiculo_id, data_inicio=None, data_fim=None):
        """Sugere melhorias na classificação baseado em padrões"""
        # Buscar eventos não aprovados (possíveis erros de classificação)
        query = EventoJornada.query.filter(
            EventoJornada.veiculo_id == veiculo_id,
            EventoJornada.aprovado == False,
            EventoJornada.classificacao_automatica == True
        )
        
        if data_inicio:
            query = query.filter(EventoJornada.data_inicio >= data_inicio)
        if data_fim:
            query = query.filter(EventoJornada.data_inicio <= data_fim)
        
        eventos_pendentes = query.all()
        
        sugestoes = []
        for evento in eventos_pendentes:
            sugestao = {
                'evento_id': evento.id,
                'tipo_atual': evento.tipo_evento.nome if evento.tipo_evento else 'N/A',
                'sugestoes': [],
                'confianca': 'baixa'
            }
            
            # Analisar se duração está fora do padrão
            if evento.duracao_minutos:
                tipo_evento = evento.tipo_evento
                if tipo_evento and tipo_evento.duracao_minima and evento.duracao_minutos < tipo_evento.duracao_minima:
                    sugestao['sugestoes'].append(f"Duração muito curta para {tipo_evento.nome}")
                elif tipo_evento and tipo_evento.duracao_maxima and evento.duracao_minutos > tipo_evento.duracao_maxima:
                    sugestao['sugestoes'].append(f"Duração muito longa para {tipo_evento.nome}")
            
            # Analisar horário vs tipo de evento
            hora = evento.data_inicio.hour
            if evento.tipo_evento and evento.tipo_evento.nome == 'Almoço':
                if not (11 <= hora <= 14 or 18 <= hora <= 21):
                    sugestao['sugestoes'].append("Horário atípico para refeição")
            
            if sugestao['sugestoes']:
                sugestoes.append(sugestao)
        
        return sugestoes


# Função utilitária para uso nas rotas
def classificar_eventos_automaticamente(veiculo_id, data_inicio=None, data_fim=None):
    """Função principal para classificação automática"""
    classificador = ClassificadorEventos()
    return classificador.processar_veiculo(veiculo_id, data_inicio, data_fim)

