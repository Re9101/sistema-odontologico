var dentistaSelect = document.getElementById('dentista_id');
var dataInput = document.getElementById('data');
var horariosContainer = document.getElementById('horarios-container');
var horaSelecionada = document.getElementById('hora_selecionada');
var form = document.getElementById('formAgendamento');

var hoje = new Date();
var ano = hoje.getFullYear();
var mes = String(hoje.getMonth() + 1).padStart(2, '0');
var dia = String(hoje.getDate()).padStart(2, '0');
dataInput.min = ano + '-' + mes + '-' + dia;

function buscarHorarios() {
    var dentistaId = dentistaSelect.value;
    var data = dataInput.value;

    if (!dentistaId || !data) {
        horariosContainer.innerHTML = '<div class="loading">Selecione um dentista e uma data</div>';
        return;
    }

    horariosContainer.innerHTML = '<div class="loading">Carregando horários...</div>';

    fetch(BUSCAR_HORARIOS_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'dentista_id=' + dentistaId + '&data=' + data
    })
    .then(function(response) { return response.json(); })
    .then(function(dados) {
        if (dados.horarios && dados.horarios.length > 0) {
            var html = '';
            dados.horarios.forEach(function(horario) {
                html += '<div class="horario-btn" data-horario="' + horario + '">' + horario + '</div>';
            });
            horariosContainer.innerHTML = html;

            document.querySelectorAll('.horario-btn').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    document.querySelectorAll('.horario-btn').forEach(function(b) { b.classList.remove('selected'); });
                    this.classList.add('selected');
                    horaSelecionada.value = this.getAttribute('data-horario');
                });
            });
        } else {
            horariosContainer.innerHTML = '<div class="loading">Nenhum horário disponível nesta data</div>';
            horaSelecionada.value = '';
        }
    })
    .catch(function(error) {
        console.error('Erro:', error);
        horariosContainer.innerHTML = '<div class="loading">Erro ao carregar horários. Tente novamente.</div>';
    });
}

form.addEventListener('submit', function(event) {
    var nome = document.getElementById('nome').value.trim();
    var telefone = document.getElementById('telefone').value.trim();
    var dentista = dentistaSelect.value;
    var data = dataInput.value;
    var hora = horaSelecionada.value;

    if (!nome) { alert('Digite seu nome completo!'); event.preventDefault(); return false; }
    if (!telefone) { alert('Digite seu telefone!'); event.preventDefault(); return false; }
    if (!dentista) { alert('Selecione um profissional!'); event.preventDefault(); return false; }
    if (!data) { alert('Selecione uma data!'); event.preventDefault(); return false; }
    if (!hora) { alert('Selecione um horário! Clique em um dos horários disponíveis.'); event.preventDefault(); return false; }

    return true;
});

dentistaSelect.addEventListener('change', function() {
    horaSelecionada.value = '';
    buscarHorarios();
});

dataInput.addEventListener('change', function() {
    horaSelecionada.value = '';
    buscarHorarios();
});

if (dentistaSelect.value) {
    buscarHorarios();
}
