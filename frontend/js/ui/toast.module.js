/*
   toast.module.js
   SRP: re-exporta window.Toast como ES module
   ✅ Usado por: ConfiguracaoController, ArenaController, FichaController
   ✅ Depende de Toast.js já carregado antes via carregar() no HTML
*/
export const Toast = window.Toast;