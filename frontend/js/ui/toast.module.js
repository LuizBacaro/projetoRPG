/*
   toast.module.js
   SRP: re-exporta window.Toast como ES module
   ✅ Usado por: ConfiguracaoController, ArenaController, FichaController
   ✅ Depende de Toast.js já ter sido carregado antes (via carregar())
*/

// ── Aguarda window.Toast estar disponível
const Toast = window.Toast;

export { Toast };