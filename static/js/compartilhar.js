function copiarLink() {
    var input = document.getElementById('linkInput');
    input.select();
    document.execCommand('copy');
    alert('Link copiado!');
}

function gerarQRCode() {
    var theme = document.documentElement.getAttribute('data-theme') || 'dark';
    var qrContainer = document.getElementById('qrCode');
    qrContainer.innerHTML = '';
    new QRCode(qrContainer, {
        text: QR_TEXT,
        width: 200,
        height: 200,
        colorDark: "#00b4d8",
        colorLight: theme === 'dark' ? "#1a1a2e" : "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
    });
}

gerarQRCode();

var observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
            gerarQRCode();
        }
    });
});
observer.observe(document.documentElement, { attributes: true });
