document.addEventListener('DOMContentLoaded', function() {
    var datePicker = document.getElementById('datePicker');
    if (datePicker) {
        datePicker.addEventListener('change', function() {
            window.location.href = AGENDAMENTOS_URL + '?data=' + this.value;
        });
    }
});

function abrirModalAgendamento() {
    document.getElementById('dataAgendamento').value = '';
    document.getElementById('modalAgendamento').style.display = 'flex';
}

function fecharModalAgendamento() {
    document.getElementById('modalAgendamento').style.display = 'none';
}

function realizarConsulta(id) {
    if (confirm('Confirmar realização desta consulta?')) {
        window.location.href = REALIZAR_CONSULTA_URL.replace('0', id);
    }
}

function cancelarConsulta(id) {
    if (confirm('Cancelar esta consulta?')) {
        window.location.href = CANCELAR_CONSULTA_URL.replace('0', id);
    }
}

window.onclick = function(event) {
    if (event.target == document.getElementById('modalAgendamento')) {
        fecharModalAgendamento();
    }
}
