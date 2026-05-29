var graficoPacientes, graficoConsultas, graficoDentistas, graficoTendencia;

function carregarDados() {
    var periodo = document.getElementById('periodo').value;
    var dataInicio = document.getElementById('data_inicio').value;
    var dataFim = document.getElementById('data_fim').value;
    var url = API_URL + '?periodo=' + periodo;
    if (dataInicio && dataFim) url += '&data_inicio=' + dataInicio + '&data_fim=' + dataFim;

    fetch(url).then(function(response) { return response.json(); }).then(function(data) {
        document.getElementById('novosPacientes').innerText = data.novos_pacientes;
        document.getElementById('consultasRealizadas').innerText = data.consultas_realizadas;
        document.getElementById('taxaOcupacao').innerText = data.taxa_ocupacao + '%';
        document.getElementById('cancelamentos').innerText = data.cancelamentos;

        var crescPac = document.getElementById('crescimentoPacientes');
        crescPac.innerHTML = (data.crescimento_pacientes >= 0 ? '↑' : '↓') + ' ' + Math.abs(data.crescimento_pacientes) + '%';
        crescPac.className = data.crescimento_pacientes >= 0 ? 'positive' : 'negative';

        var crescCons = document.getElementById('crescimentoConsultas');
        crescCons.innerHTML = (data.crescimento_consultas >= 0 ? '↑' : '↓') + ' ' + Math.abs(data.crescimento_consultas) + '%';
        crescCons.className = data.crescimento_consultas >= 0 ? 'positive' : 'negative';

        document.getElementById('taxaCancelamento').innerHTML = data.taxa_cancelamento + '% das consultas';

        if (graficoPacientes) graficoPacientes.destroy();
        graficoPacientes = new Chart(document.getElementById('graficoPacientes'), {
            type: 'line', data: { labels: data.dias, datasets: [{ label: 'Novos Pacientes', data: data.pacientes_por_dia, borderColor: '#00b4d8', backgroundColor: 'rgba(0,180,216,0.1)', fill: true, tension: 0.4 }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'top', labels: { color: 'white', font: { size: 10 } } } } }
        });

        if (graficoConsultas) graficoConsultas.destroy();
        graficoConsultas = new Chart(document.getElementById('graficoConsultas'), {
            type: 'bar', data: { labels: data.dias, datasets: [{ label: 'Consultas', data: data.consultas_por_dia, backgroundColor: '#28a745', borderRadius: 6 }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'top', labels: { color: 'white', font: { size: 10 } } } } }
        });

        if (graficoDentistas) graficoDentistas.destroy();
        if (data.dentistas_nomes.length > 0) {
            graficoDentistas = new Chart(document.getElementById('graficoDentistas'), {
                type: 'pie', data: { labels: data.dentistas_nomes, datasets: [{ data: data.dentistas_consultas, backgroundColor: ['#00b4d8', '#0077b6', '#20c997', '#ffc107', '#dc3545'] }] },
                options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'right', labels: { color: 'white', font: { size: 10 } } } } }
            });
        }

        if (graficoTendencia) graficoTendencia.destroy();
        graficoTendencia = new Chart(document.getElementById('graficoTendencia'), {
            type: 'line', data: { labels: data.meses, datasets: [{ label: 'Pacientes', data: data.pacientes_por_mes, borderColor: '#00b4d8', tension: 0.4 }, { label: 'Consultas', data: data.consultas_por_mes, borderColor: '#28a745', tension: 0.4 }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'top', labels: { color: 'white', font: { size: 10 } } } } }
        });

        var html = '';
        for (var i = 0; i < data.meses.length; i++) {
            var variacao = i > 0 ? data.pacientes_por_mes[i] - data.pacientes_por_mes[i-1] : 0;
            html += '<tr><td>' + data.meses[i] + '</td><td>' + data.pacientes_por_mes[i] + '</td><td class="' + (variacao >= 0 ? 'positive' : 'negative') + '">' + (variacao >= 0 ? '↑' : '↓') + ' ' + Math.abs(variacao) + '</td></tr>';
        }
        document.getElementById('corpoTabelaPacientes').innerHTML = html;

        var htmlTop = '';
        for (var p of data.top_pacientes) {
            htmlTop += '<tr><td><strong>' + p.nome + '</strong></td><td>' + p.total + ' consultas</td><td>' + (p.ultima || '-') + '</td></tr>';
        }
        document.getElementById('corpoTopPacientes').innerHTML = htmlTop;
    }).catch(function(error) { console.error('Erro:', error); });
}

function aplicarFiltro() { carregarDados(); }

function exportarExcel() {
    var params = new URLSearchParams({
        periodo: document.getElementById('periodo').value,
        data_inicio: document.getElementById('data_inicio').value,
        data_fim: document.getElementById('data_fim').value
    });
    window.location.href = PRINT_URL + '?' + params.toString();
}
