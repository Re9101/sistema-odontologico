function mostrarRecuperarSenha() {
    document.getElementById('modalRecuperar').style.display = 'flex';
}

function fecharModalRecuperar() {
    document.getElementById('modalRecuperar').style.display = 'none';
}

window.onclick = function(event) {
    if (event.target == document.getElementById('modalRecuperar')) {
        fecharModalRecuperar();
    }
}
