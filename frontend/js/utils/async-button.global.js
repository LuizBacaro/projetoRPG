(function () {
    function setLoading(button, loading, options) {
        if (!button) return;

        var opts = options || {};
        var loadingText = opts.loadingText || 'Salvando...';
        var idleText = opts.idleText;

        if (loading) {
            if (!button.dataset.originalText) {
                button.dataset.originalText = button.textContent || '';
            }
            if (!button.dataset.originalDisabled) {
                button.dataset.originalDisabled = button.disabled ? 'true' : 'false';
            }

            button.disabled = true;
            button.classList.add('is-loading');
            button.setAttribute('aria-busy', 'true');
            button.textContent = loadingText;
            return;
        }

        var wasOriginallyDisabled = button.dataset.originalDisabled === 'true';
        var originalText = button.dataset.originalText || button.textContent || '';

        button.disabled = wasOriginallyDisabled;
        button.classList.remove('is-loading');
        button.setAttribute('aria-busy', 'false');
        button.textContent = typeof idleText === 'string' ? idleText : originalText;

        delete button.dataset.originalText;
        delete button.dataset.originalDisabled;
    }

    async function run(button, options, asyncAction) {
        if (typeof asyncAction !== 'function') {
            throw new Error('AsyncButtonState.run requer uma acao assincrona.');
        }

        if (!button) {
            return asyncAction();
        }

        setLoading(button, true, options);
        try {
            return await asyncAction();
        } finally {
            setLoading(button, false, options);
        }
    }

    window.AsyncButtonState = {
        setLoading: setLoading,
        run: run,
    };
})();
