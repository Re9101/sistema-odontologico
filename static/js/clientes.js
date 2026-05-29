function abrirModalNovo() {
    document.getElementById('modalNovo').style.display = 'flex';
}

function fecharModalNovo() {
    document.getElementById('modalNovo').style.display = 'none';
}

function abrirModalEditar(id, nome, telefone, email, data_nascimento, convenio, alergias) {
    document.getElementById('edit_nome').value = nome;
    document.getElementById('edit_telefone').value = telefone;
    document.getElementById('edit_email').value = email || '';
    document.getElementById('edit_data_nascimento').value = data_nascimento || '';
    document.getElementById('edit_convenio').value = convenio || '';
    document.getElementById('edit_alergias').value = alergias || '';

    var form = document.getElementById('formEditar');
    form.action = EDITAR_CLIENTE_URL.replace('0', id);

    document.getElementById('modalEditar').style.display = 'flex';
}

function fecharModalEditar() {
    document.getElementById('modalEditar').style.display = 'none';
}

function excluirCliente(id) {
    if (confirm('Tem certeza que deseja excluir este cliente?\n\nEsta ação não pode ser desfeita.')) {
        window.location.href = EXCLUIR_CLIENTE_URL.replace('0', id);
    }
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}
