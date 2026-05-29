function abrirModalNovo() {
    document.getElementById('modalNovo').style.display = 'flex';
}

function fecharModalNovo() {
    document.getElementById('modalNovo').style.display = 'none';
}

function abrirModalEditar(id, nome, cro, especialidade, telefone, email) {
    document.getElementById('edit_nome').value = nome;
    document.getElementById('edit_cro').value = cro;
    document.getElementById('edit_especialidade').value = especialidade || '';
    document.getElementById('edit_telefone').value = telefone || '';
    document.getElementById('edit_email').value = email || '';

    var form = document.getElementById('formEditar');
    form.action = EDITAR_DENTISTA_URL.replace('0', id);

    document.getElementById('modalEditar').style.display = 'flex';
}

function fecharModalEditar() {
    document.getElementById('modalEditar').style.display = 'none';
}

function excluirDentista(id) {
    if (confirm('Tem certeza que deseja excluir este dentista?\n\nSe ele tiver consultas vinculadas, será apenas desativado.')) {
        window.location.href = EXCLUIR_DENTISTA_URL.replace('0', id);
    }
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}
