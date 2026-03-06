/**
 * Entry Point da Aplicação Frontend — Arena de Combate
 * SRP: inicialização e orquestração dos controllers da Arena APENAS
 *
 * Responsabilidades REMOVIDAS (movidas para DashboardController):
 *   - ModalCadastro (jogador, monstro, npc)
 *   - TipoSelector
 *   - Botão "Adicionar Combatente"
 *
 * Arquivos globais (via <script> no index.html, SEM type="module"):
 *   - DanoCuraService.js
 *   - ModalDanoCura.js
 *   - CondicaoService.js
 *   - CondicaoUI.js (contém class ModalCondicao)
 */
import { ConfiguracaoController } from './controllers/ConfiguracaoController.js';
import { ArenaController }        from './controllers/ArenaController.js';
import { ModalEdicao }            from './ui/ModalEdicao.js';
import { ArenaAtaquesMagias }     from './ui/ArenaAtaquesMagias.js';
import { atualizarModificadorDOM } from './utils/dnd.js';

const app = { controllers: {}, modals: {} };

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎮 Arena de Combate TTRPG - Iniciando...');

    // ── Proteção JWT 
    // AuthService é carregado como global via <script> antes do main.js
    if (typeof AuthService !== 'undefined') {
        AuthService.exigirLogin();
        _exibirUsuarioHeader();
    }

    // ── Controllers 
    app.controllers.configuracao = new ConfiguracaoController();
    app.controllers.arena        = new ArenaController();

    // ── Modal de Edição 
    // Cadastro foi movido para o Dashboard
    app.modals.edicao = new ModalEdicao();

    // ── Modal Dano/Cura (classe global via <script>) ──────────────────────
    if (typeof DanoCuraService !== 'undefined' && typeof ModalDanoCura !== 'undefined') {
        try {
            window.modalDanoCuraInstance = new ModalDanoCura(
                new DanoCuraService(),
                app.controllers.arena
            );
            console.log('✅ Modal de Dano/Cura inicializado');
        } catch (error) {
            console.error('❌ Erro ao inicializar Modal de Dano/Cura:', error);
        }
    }

    // ── Modal Condição (classe global via <script>) ───────────────────────
    if (typeof ModalCondicao !== 'undefined' && typeof CondicaoService !== 'undefined') {
        try {
            window.modalCondicaoInstance = new ModalCondicao(
                new CondicaoService('/api'),
                app.controllers.arena
            );
            console.log('✅ Modal de Condição inicializado');
        } catch (error) {
            console.error('❌ Erro ao inicializar Modal de Condição:', error);
        }
    }

    // ── Eventos de recarregamento após CRUD no Dashboard ──────────────────
    _configurarEventosRecarregamento();

    // ── Evento: combatente ativo mudou → renderiza ataques e magias ───────
    //
    // Disparado pelo ArenaController toda vez que o turno avança
    // ou o combate é iniciado. Recebe o combatente ativo no detail.
    //
    // Regra de negócio:
    //   jogador  → exibe ataques e magias cadastrados no Dashboard
    //   monstro  → exibe ataques (se houver), sem magias
    //   npc      → exibe ataques (se houver), sem magias

    document.addEventListener('combatenteAtivoMudou', (e) => {
        const combatente = e.detail?.combatente;
        if (!combatente) return;

        const isJogador = combatente.tipo === 'jogador';

        // Renderiza ataques — para todos os tipos
        ArenaAtaquesMagias.renderAtaques(
            combatente.ataques || [],
            'arenaAtaquesContainer'
        );

        // Renderiza magias — apenas para jogadores
        ArenaAtaquesMagias.renderMagias(
            isJogador ? (combatente.magias_slots || []) : [],
            'arenaMagiasContainer',
            async (slotId, nivel, usados) => {
                // Persiste usados no banco em tempo real via PATCH
                if (!slotId) return; // slot sem id = nível zerado, ignora

                try {
                    const token = sessionStorage.getItem('rpg_token');
                    await fetch(`/api/magias_slots/${slotId}/usados`, {
                        method:  'PATCH',
                        headers: {
                            'Content-Type':  'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({ usados })
                    });
                } catch (err) {
                    console.error('❌ Erro ao persistir slot de magia:', err);
                }
            }
        );
    });

    // ── Funções globais expostas para HTML inline ─────────────────────────
    window.atualizarModificador = atualizarModificadorDOM;
    window.fecharModalEdicao    = () => app.modals.edicao.fechar();
    window.confirmarDelecao     = () => app.modals.edicao.deletar();
    window.removerImagemEdicao  = () => _removerImagemUpload('', true);

    window.abrirModalDanoCura = () => {
        window.modalDanoCuraInstance
            ? window.modalDanoCuraInstance.abrir()
            : console.error('❌ modalDanoCuraInstance não inicializado');
    };

    window.abrirModalCondicao = () => {
        window.modalCondicaoInstance
            ? window.modalCondicaoInstance.abrir()
            : console.error('❌ modalCondicaoInstance não inicializado');
    };

    console.log('✅ Arena inicializada com sucesso!');
});

// ── Exibe nome e perfil do usuário no header da arena ────────────────────────

function _exibirUsuarioHeader() {
    const nomeEl   = document.getElementById('nomeUsuarioArena');
    const badgeEl  = document.getElementById('badgePerfilArena');
    const logoutEl = document.getElementById('btnLogoutArena');

    if (nomeEl)   nomeEl.textContent  = AuthService.getNome();
    if (badgeEl)  badgeEl.textContent = AuthService.getPerfil();
    if (logoutEl) logoutEl.addEventListener('click', () => AuthService.logout());
}

// ── Eventos de recarregamento após CRUD no Dashboard ─────────────────────────

function _configurarEventosRecarregamento() {
    // Recarrega lista quando combatente é criado/editado/deletado no Dashboard
    ['combatenteCriado', 'combatenteAtualizado', 'combatenteDeletado'].forEach(evento => {
        document.addEventListener(evento, () => {
            app.controllers.configuracao.carregarCombatentes();
            app.controllers.configuracao.atualizarSelecionados();
        });
    });

    // Volta para configuração ao sair da arena
    document.addEventListener('voltarConfiguracao', () => {
        app.controllers.configuracao.carregarCombatentes();
        app.controllers.configuracao.combatentesSelecionados = [];
        app.controllers.configuracao.atualizarSelecionados();
    });
}

// ── Helper de remoção de imagem (edição) ─────────────────────────────────────

function _removerImagemUpload(sufixo = '', isEdit = false) {
    const prefix      = isEdit ? 'edit' : 'input';
    const input       = document.getElementById(`${prefix}Foto${sufixo}`);
    const placeholder = document.getElementById(
        isEdit ? `${prefix}UploadPlaceholder` : `uploadPlaceholder${sufixo}`
    );
    const preview = document.getElementById(
        isEdit ? `${prefix}UploadPreview` : `uploadPreview${sufixo}`
    );

    if (input)       input.value             = '';
    if (placeholder) placeholder.style.display = 'flex';
    if (preview)     preview.style.display     = 'none';
}

export { app };
window.app = app;