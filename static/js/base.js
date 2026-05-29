document.addEventListener('DOMContentLoaded', function() {
    var dateEl = document.getElementById('currentDate');
    if (dateEl) {
        dateEl.innerText = new Date().toLocaleDateString('pt-BR');
    }
    atualizarIconeTema();
});

function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.querySelector('.sidebar-overlay');
    if (sidebar) { sidebar.classList.toggle('open'); }
    if (overlay) { overlay.classList.toggle('active'); }
}

function toggleTheme() {
    var html = document.documentElement;
    var current = html.getAttribute('data-theme') || 'dark';
    var next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    atualizarIconeTema();
}

function atualizarIconeTema() {
    var theme = document.documentElement.getAttribute('data-theme') || 'dark';
    var icon = document.getElementById('themeIcon');
    var label = document.getElementById('themeLabel');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    }
    if (label) {
        label.textContent = theme === 'dark' ? 'Escuro' : 'Claro';
    }
}

if (window.innerWidth <= 768) {
    document.querySelectorAll('.nav-item').forEach(function(item) {
        item.addEventListener('click', function() { toggleSidebar(); });
    });
}
