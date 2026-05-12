/**
 * Vercel (e `vercel build` local): gera `frontend/js/shared/render-api-origin-boot.js`
 * a partir de ARENA_RENDER_API_ORIGIN.
 *
 * No painel Vercel → Settings → Environment Variables:
 *   - Production: ARENA_RENDER_API_ORIGIN = https://<api-prod>.onrender.com
 *   - Preview:    ARENA_RENDER_API_ORIGIN = https://projetorpg-dev.onrender.com (ou outra API de homolog)
 *   - Development (opcional): mesmo que Preview para `vercel dev`
 *
 * Se a variável não existir no build, mantém o default abaixo (API de produção atual no repo).
 *
 * Nota: no repositório, `render-api-origin-boot.js` usa `location.origin` em hosts que não são
 * Vercel nem o domínio Arena (ex.: outro serviço Render com front+API no mesmo URL). O build
 * da Vercel substitui este ficheiro por uma única origem explícita.
 */
const fs = require("fs");
const path = require("path");

const DEFAULT_ORIGIN = "https://projetorpg-7ih3.onrender.com";

let origin = (process.env.ARENA_RENDER_API_ORIGIN || "").trim() || DEFAULT_ORIGIN;
try {
    const u = new URL(origin);
    if (
        u.hostname === "arena-de-combate-rpg.com.br" ||
        u.hostname === "www.arena-de-combate-rpg.com.br"
    ) {
        console.warn(
            "[inject-render-api-origin] ARENA_RENDER_API_ORIGIN aponta para o site estático (apex/www). " +
                "A API está no Render — a usar DEFAULT:",
            DEFAULT_ORIGIN
        );
        origin = DEFAULT_ORIGIN;
    }
} catch (_e) {
    console.warn(
        "[inject-render-api-origin] ARENA_RENDER_API_ORIGIN inválida — a usar DEFAULT:",
        DEFAULT_ORIGIN
    );
    origin = DEFAULT_ORIGIN;
}

const target = path.join(
    __dirname,
    "..",
    "frontend",
    "js",
    "shared",
    "render-api-origin-boot.js"
);

const content = `/**
 * Origem HTTPS da API (Render). Gerado em build por scripts/inject-render-api-origin.cjs.
 * Em desenvolvimento local sem rebuild, podes editar este ficheiro à mão.
 */
(function (g) {
    g.__ARENA_RENDER_API_ORIGIN__ = ${JSON.stringify(origin)};
})(typeof window !== "undefined" ? window : typeof globalThis !== "undefined" ? globalThis : self);
`;

fs.writeFileSync(target, content, "utf8");
console.log(`[inject-render-api-origin] ${target} -> ${origin}`);
