document.addEventListener('DOMContentLoaded', function() {
    var el = document.querySelector('.periodo-item:last-child span strong');
    if (el) {
        el.innerText = new Date().toLocaleDateString('pt-BR') + ' ' + new Date().toLocaleTimeString('pt-BR');
    }
});

function fecharJanela() {
    window.close();
    setTimeout(function() {
        window.history.back();
    }, 300);
}
