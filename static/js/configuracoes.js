function editarUsuario(id, username, nome, email, celular, tipo, ativo) {
    document.getElementById('formEditar').action = EDITAR_USUARIO_URL.replace('0', id);
    document.getElementById('edit_username').value = username;
    document.getElementById('edit_nome').value = nome;
    document.getElementById('edit_email').value = email;
    document.getElementById('edit_celular').value = celular;
    document.getElementById('edit_tipo').value = tipo;
    document.getElementById('edit_ativo').checked = ativo == 1;
    document.getElementById('modalEditar').style.display = 'flex';
}
function fecharModalEditar() { document.getElementById('modalEditar').style.display = 'none'; }
window.onclick = function(event) {
    if (event.target == document.getElementById('modalEditar')) fecharModalEditar();
}
