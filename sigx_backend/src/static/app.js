// SIGx Automatização - Frontend JavaScript
class SigxApp {
    constructor() {
        this.baseUrl = window.location.origin;
        this.currentTab = 'dashboard';
        this.veiculos = [];
        this.tiposEvento = [];
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadInitialData();
        this.showTab('dashboard');
    }

    setupEventListeners() {
        // Navigation tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.showTab(tabName);
            });
        });

        // Modal controls
        document.getElementById('btn-fechar-modal').addEventListener('click', () => {
            this.closeModal();
        });
        document.getElementById('btn-cancelar').addEventListener('click', () => {
            this.closeModal();
        });

        // Form submissions
        document.getElementById('form-evento').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveEvento();
        });

        // Buttons
        document.getElementById('btn-atualizar-eventos').addEventListener('click', () => {
            this.loadEventos();
        });
        document.getElementById('btn-classificar-posicoes').addEventListener('click', () => {
            this.classificarPosicoes();
        });
        document.getElementById('btn-importar').addEventListener('click', () => {
            this.importarPosicoes();
        });

        // File input
        document.getElementById('arquivo-posicoes').addEventListener('change', (e) => {
            const btn = document.getElementById('btn-importar');
            btn.disabled = !e.target.files.length;
        });

        // Filters
        document.getElementById('filtro-veiculo').addEventListener('change', () => {
            this.loadEventos();
        });
        document.getElementById('filtro-status').addEventListener('change', () => {
            this.loadEventos();
        });
        document.getElementById('posicoes-veiculo').addEventListener('change', () => {
            this.loadPosicoes();
        });
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadVeiculos(),
                this.loadTiposEvento(),
                this.loadExemploImportacao()
            ]);
            this.populateSelects();
        } catch (error) {
            console.error('Erro ao carregar dados iniciais:', error);
            this.showError('Erro ao carregar dados iniciais');
        }
    }

    async loadVeiculos() {
        try {
            const response = await fetch(`${this.baseUrl}/api/veiculos/listar`);
            const data = await response.json();
            this.veiculos = data.veiculos || [];
        } catch (error) {
            console.error('Erro ao carregar veículos:', error);
        }
    }

    async loadTiposEvento() {
        try {
            const response = await fetch(`${this.baseUrl}/api/eventos/tipos`);
            const data = await response.json();
            this.tiposEvento = data.tipos_evento || [];
        } catch (error) {
            console.error('Erro ao carregar tipos de evento:', error);
        }
    }

    async loadExemploImportacao() {
        try {
            const response = await fetch(`${this.baseUrl}/api/posicoes/exemplo-importacao`);
            const data = await response.json();
            document.getElementById('exemplo-json').textContent = JSON.stringify(data.exemplo, null, 2);
        } catch (error) {
            console.error('Erro ao carregar exemplo:', error);
        }
    }

    populateSelects() {
        // Populate vehicle selects
        const selects = ['filtro-veiculo', 'posicoes-veiculo'];
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            select.innerHTML = selectId === 'filtro-veiculo' ? '<option value="">Todos os Veículos</option>' : '<option value="">Selecione um Veículo</option>';
            
            this.veiculos.forEach(veiculo => {
                const option = document.createElement('option');
                option.value = veiculo.id;
                option.textContent = `${veiculo.placa} - ${veiculo.identificador || 'N/A'}`;
                select.appendChild(option);
            });
        });

        // Populate event types
        const tipoSelect = document.getElementById('evento-tipo');
        tipoSelect.innerHTML = '';
        this.tiposEvento.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.id;
            option.textContent = tipo.nome;
            tipoSelect.appendChild(option);
        });
    }

    showTab(tabName) {
        // Update navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active', 'border-blue-500', 'text-blue-600');
            tab.classList.add('border-transparent', 'text-gray-500');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active', 'border-blue-500', 'text-blue-600');
        document.querySelector(`[data-tab="${tabName}"]`).classList.remove('border-transparent', 'text-gray-500');

        // Show/hide content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        document.getElementById(`${tabName}-tab`).classList.remove('hidden');

        this.currentTab = tabName;

        // Load data for specific tabs
        switch (tabName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'eventos':
                this.loadEventos();
                break;
            case 'veiculos':
                this.loadVeiculosTab();
                break;
        }
    }

    async loadDashboard() {
        try {
            // Load statistics
            const response = await fetch(`${this.baseUrl}/api/eventos/estatisticas`);
            const data = await response.json();
            
            if (data.estatisticas) {
                document.getElementById('eventos-hoje').textContent = data.estatisticas.total_eventos || 0;
                document.getElementById('eventos-aprovados').textContent = data.estatisticas.eventos_aprovados || 0;
                document.getElementById('eventos-pendentes').textContent = data.estatisticas.eventos_pendentes || 0;
                document.getElementById('eventos-automaticos').textContent = data.estatisticas.eventos_automaticos || 0;
            }

            // Load charts
            this.loadCharts(data);
            
            // Load recent events
            this.loadEventosRecentes();
        } catch (error) {
            console.error('Erro ao carregar dashboard:', error);
        }
    }

    loadCharts(data) {
        // Chart by type
        const ctxTipos = document.getElementById('chart-tipos').getContext('2d');
        const tiposData = data.por_tipo || {};
        
        new Chart(ctxTipos, {
            type: 'doughnut',
            data: {
                labels: Object.keys(tiposData),
                datasets: [{
                    data: Object.values(tiposData),
                    backgroundColor: [
                        '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
                        '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Timeline chart (placeholder)
        const ctxTimeline = document.getElementById('chart-timeline').getContext('2d');
        new Chart(ctxTimeline, {
            type: 'line',
            data: {
                labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
                datasets: [{
                    label: 'Eventos',
                    data: [12, 19, 3, 5, 2, 3, 9],
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    async loadEventosRecentes() {
        try {
            const response = await fetch(`${this.baseUrl}/api/eventos/listar`);
            const data = await response.json();
            
            const container = document.getElementById('eventos-recentes');
            container.innerHTML = '';
            
            const eventos = data.eventos.slice(0, 5); // Últimos 5 eventos
            
            eventos.forEach(evento => {
                const div = document.createElement('div');
                div.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg';
                div.innerHTML = `
                    <div class="flex items-center space-x-3">
                        <div class="w-3 h-3 rounded-full" style="background-color: ${evento.tipo_evento?.cor_hex || '#6B7280'}"></div>
                        <div>
                            <p class="font-medium text-gray-900">${evento.tipo_evento?.nome || 'N/A'}</p>
                            <p class="text-sm text-gray-500">${evento.veiculo?.placa || 'N/A'} - ${this.formatDateTime(evento.data_inicio)}</p>
                        </div>
                    </div>
                    <span class="status-badge ${evento.aprovado ? 'status-aprovado' : 'status-pendente'}">
                        ${evento.aprovado ? 'Aprovado' : 'Pendente'}
                    </span>
                `;
                container.appendChild(div);
            });
        } catch (error) {
            console.error('Erro ao carregar eventos recentes:', error);
        }
    }

    async loadEventos() {
        try {
            const veiculoId = document.getElementById('filtro-veiculo').value;
            const aprovado = document.getElementById('filtro-status').value;
            
            let url = `${this.baseUrl}/api/eventos/listar?`;
            if (veiculoId) url += `veiculo_id=${veiculoId}&`;
            if (aprovado) url += `aprovado=${aprovado}&`;
            
            const response = await fetch(url);
            const data = await response.json();
            
            const container = document.getElementById('lista-eventos');
            container.innerHTML = '';
            
            data.eventos.forEach(evento => {
                const div = document.createElement('div');
                div.className = 'border border-gray-200 rounded-lg p-4 hover:bg-gray-50';
                div.innerHTML = `
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-4">
                            <div class="w-4 h-4 rounded-full" style="background-color: ${evento.tipo_evento?.cor_hex || '#6B7280'}"></div>
                            <div>
                                <h4 class="font-medium text-gray-900">${evento.tipo_evento?.nome || 'N/A'}</h4>
                                <p class="text-sm text-gray-500">
                                    ${evento.veiculo?.placa || 'N/A'} - ${evento.motorista?.nome || 'N/A'}
                                </p>
                                <p class="text-sm text-gray-500">
                                    ${this.formatDateTime(evento.data_inicio)} - ${this.formatDateTime(evento.data_fim)}
                                    ${evento.duracao_minutos ? `(${evento.duracao_minutos} min)` : ''}
                                </p>
                            </div>
                        </div>
                        <div class="flex items-center space-x-2">
                            <span class="status-badge ${evento.aprovado ? 'status-aprovado' : 'status-pendente'}">
                                ${evento.aprovado ? 'Aprovado' : 'Pendente'}
                            </span>
                            ${evento.classificacao_automatica ? '<span class="status-badge status-automatico">Auto</span>' : ''}
                            <button onclick="app.editEvento(${evento.id})" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-edit"></i>
                            </button>
                            ${!evento.aprovado ? `<button onclick="app.aprovarEvento(${evento.id})" class="text-green-600 hover:text-green-800">
                                <i class="fas fa-check"></i>
                            </button>` : ''}
                        </div>
                    </div>
                    ${evento.observacoes ? `<p class="mt-2 text-sm text-gray-600">${evento.observacoes}</p>` : ''}
                `;
                container.appendChild(div);
            });
        } catch (error) {
            console.error('Erro ao carregar eventos:', error);
        }
    }

    async loadPosicoes() {
        const veiculoId = document.getElementById('posicoes-veiculo').value;
        if (!veiculoId) return;

        try {
            // Load statistics
            const statsResponse = await fetch(`${this.baseUrl}/api/posicoes/estatisticas/${veiculoId}`);
            const statsData = await statsResponse.json();
            
            if (statsData.estatisticas) {
                const container = document.getElementById('estatisticas-posicoes');
                container.innerHTML = `
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div class="bg-blue-50 p-3 rounded-lg">
                            <p class="text-sm text-blue-600">Total Posições</p>
                            <p class="text-lg font-bold text-blue-900">${statsData.estatisticas.total_posicoes}</p>
                        </div>
                        <div class="bg-green-50 p-3 rounded-lg">
                            <p class="text-sm text-green-600">Processadas</p>
                            <p class="text-lg font-bold text-green-900">${statsData.estatisticas.posicoes_processadas}</p>
                        </div>
                        <div class="bg-yellow-50 p-3 rounded-lg">
                            <p class="text-sm text-yellow-600">Distância (km)</p>
                            <p class="text-lg font-bold text-yellow-900">${statsData.estatisticas.distancia_total_km}</p>
                        </div>
                        <div class="bg-purple-50 p-3 rounded-lg">
                            <p class="text-sm text-purple-600">Vel. Média</p>
                            <p class="text-lg font-bold text-purple-900">${statsData.estatisticas.velocidade_media_kmh} km/h</p>
                        </div>
                    </div>
                `;
            }

            // Load positions
            const posResponse = await fetch(`${this.baseUrl}/api/posicoes/veiculo/${veiculoId}?limite=50`);
            const posData = await posResponse.json();
            
            const container = document.getElementById('lista-posicoes');
            container.innerHTML = '';
            
            posData.posicoes.forEach(posicao => {
                const div = document.createElement('div');
                div.className = `flex items-center justify-between p-2 border-l-4 ${posicao.processado ? 'border-green-500 bg-green-50' : 'border-yellow-500 bg-yellow-50'}`;
                div.innerHTML = `
                    <div>
                        <p class="text-sm font-medium">${this.formatDateTime(posicao.data_hora)}</p>
                        <p class="text-xs text-gray-600">${posicao.endereco || 'N/A'}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-sm">${posicao.velocidade} km/h</p>
                        <p class="text-xs ${posicao.processado ? 'text-green-600' : 'text-yellow-600'}">
                            ${posicao.processado ? 'Processado' : 'Pendente'}
                        </p>
                    </div>
                `;
                container.appendChild(div);
            });
        } catch (error) {
            console.error('Erro ao carregar posições:', error);
        }
    }

    async loadVeiculosTab() {
        const container = document.getElementById('lista-veiculos');
        container.innerHTML = '';
        
        this.veiculos.forEach(veiculo => {
            const div = document.createElement('div');
            div.className = 'bg-white border border-gray-200 rounded-lg p-4 card-hover';
            div.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <h4 class="font-bold text-lg text-gray-900">${veiculo.placa}</h4>
                    <span class="status-badge ${veiculo.ativo ? 'status-aprovado' : 'status-pendente'}">
                        ${veiculo.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                </div>
                <p class="text-sm text-gray-600 mb-1">ID: ${veiculo.identificador || 'N/A'}</p>
                <p class="text-sm text-gray-600">Motorista: ${veiculo.motorista?.nome || 'Não atribuído'}</p>
            `;
            container.appendChild(div);
        });
    }

    async editEvento(eventoId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/eventos/${eventoId}`);
            const evento = await response.json();
            
            // Populate form
            document.getElementById('evento-id').value = evento.id;
            document.getElementById('evento-tipo').value = evento.tipo_evento_id;
            document.getElementById('evento-status').value = evento.aprovado;
            document.getElementById('evento-inicio').value = this.formatDateTimeInput(evento.data_inicio);
            document.getElementById('evento-fim').value = this.formatDateTimeInput(evento.data_fim);
            document.getElementById('evento-observacoes').value = evento.observacoes || '';
            
            this.showModal();
        } catch (error) {
            console.error('Erro ao carregar evento:', error);
            this.showError('Erro ao carregar evento');
        }
    }

    async saveEvento() {
        try {
            this.showLoading();
            
            const eventoId = document.getElementById('evento-id').value;
            const data = {
                tipo_evento_id: parseInt(document.getElementById('evento-tipo').value),
                data_inicio: document.getElementById('evento-inicio').value,
                data_fim: document.getElementById('evento-fim').value,
                observacoes: document.getElementById('evento-observacoes').value
            };
            
            const response = await fetch(`${this.baseUrl}/api/eventos/${eventoId}/atualizar`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.closeModal();
                this.loadEventos();
                this.showSuccess('Evento atualizado com sucesso');
                
                // Approve if status changed
                const aprovado = document.getElementById('evento-status').value === 'true';
                if (aprovado) {
                    await this.aprovarEvento(eventoId);
                }
            } else {
                throw new Error('Erro ao salvar evento');
            }
        } catch (error) {
            console.error('Erro ao salvar evento:', error);
            this.showError('Erro ao salvar evento');
        } finally {
            this.hideLoading();
        }
    }

    async aprovarEvento(eventoId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/eventos/${eventoId}/aprovar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ usuario: 'Sistema' })
            });
            
            if (response.ok) {
                this.loadEventos();
                this.showSuccess('Evento aprovado com sucesso');
            } else {
                throw new Error('Erro ao aprovar evento');
            }
        } catch (error) {
            console.error('Erro ao aprovar evento:', error);
            this.showError('Erro ao aprovar evento');
        }
    }

    async classificarPosicoes() {
        const veiculoId = document.getElementById('posicoes-veiculo').value;
        if (!veiculoId) {
            this.showError('Selecione um veículo');
            return;
        }

        try {
            this.showLoading();
            
            const response = await fetch(`${this.baseUrl}/api/posicoes/classificar/${veiculoId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showSuccess(`${data.eventos_classificados} eventos classificados automaticamente`);
                this.loadPosicoes();
            } else {
                throw new Error(data.erro || 'Erro na classificação');
            }
        } catch (error) {
            console.error('Erro na classificação:', error);
            this.showError('Erro na classificação automática');
        } finally {
            this.hideLoading();
        }
    }

    async importarPosicoes() {
        const fileInput = document.getElementById('arquivo-posicoes');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showError('Selecione um arquivo');
            return;
        }

        try {
            this.showLoading();
            
            const text = await file.text();
            const data = JSON.parse(text);
            
            // Add classification flag
            data.classificar_automaticamente = document.getElementById('classificar-automatico').checked;
            
            const response = await fetch(`${this.baseUrl}/api/posicoes/importar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                const container = document.getElementById('resultado-importacao');
                container.className = 'mt-6 p-4 bg-green-50 border border-green-200 rounded-lg';
                container.innerHTML = `
                    <h4 class="font-medium text-green-900 mb-2">Importação Concluída</h4>
                    <p class="text-sm text-green-700">Posições importadas: ${result.posicoes_importadas}</p>
                    <p class="text-sm text-green-700">Posições duplicadas: ${result.posicoes_duplicadas}</p>
                    ${result.eventos_classificados ? `<p class="text-sm text-green-700">Eventos classificados: ${result.eventos_classificados}</p>` : ''}
                `;
                container.classList.remove('hidden');
                
                // Clear file input
                fileInput.value = '';
                document.getElementById('btn-importar').disabled = true;
            } else {
                throw new Error(result.erro || 'Erro na importação');
            }
        } catch (error) {
            console.error('Erro na importação:', error);
            this.showError('Erro na importação: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    showModal() {
        document.getElementById('modal-evento').classList.add('active');
    }

    closeModal() {
        document.getElementById('modal-evento').classList.remove('active');
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.add('active');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('active');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Simple notification - could be enhanced with a proper notification system
        const color = type === 'success' ? 'green' : 'red';
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 bg-${color}-100 border border-${color}-400 text-${color}-700 px-4 py-3 rounded z-50`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    }

    formatDateTimeInput(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toISOString().slice(0, 16);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SigxApp();
});

