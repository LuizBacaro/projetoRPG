class Toast {
    static success(texto) { Toast.mostrar(texto, 'success'); }
    static error(texto)   { Toast.mostrar(texto, 'error');   }
    static warning(texto) { Toast.mostrar(texto, 'warning'); }
    static info(texto)    { Toast.mostrar(texto, 'info');    }

    static mostrar(texto, tipo) {
        if (!tipo) tipo = 'info';
        Toast._injetarEstilos();
        var el = document.createElement('div');
        el.className   = 'toast toast-' + tipo;
        el.textContent = texto;
        document.body.appendChild(el);
        setTimeout(function() { el.classList.add('show'); }, 50);
        setTimeout(function() {
            el.classList.remove('show');
            setTimeout(function() { el.remove(); }, 300);
        }, 3000);
    }

    static _injetarEstilos() {
        if (document.getElementById('toast-styles')) return;
        var s = document.createElement('style');
        s.id = 'toast-styles';
        var c = '';
        c += '.toast{position:fixed;bottom:1.5rem;right:1.5rem;';
        c += 'padding:.75rem 1.25rem;border-radius:.5rem;color:#fff;';
        c += 'font-size:.9rem;font-weight:500;opacity:0;';
        c += 'transform:translateY(1rem);';
        c += 'transition:opacity .3s,transform .3s;';
        c += 'z-index:9999;max-width:360px;';
        c += 'box-shadow:0 4px 12px rgba(0,0,0,.4);}';
        c += '.toast.show{opacity:1;transform:translateY(0);}';
        c += '.toast-success{background:#059669;}';
        c += '.toast-error{background:#dc2626;}';
        c += '.toast-warning{background:#d97706;}';
        c += '.toast-info{background:#2563eb;}';
        s.textContent = c;
        document.head.appendChild(s);
    }
}

window.Toast = Toast;