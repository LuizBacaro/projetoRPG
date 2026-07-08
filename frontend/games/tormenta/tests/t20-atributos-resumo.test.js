const assert = require('assert');
const path = require('path');

const helper = require(path.join(__dirname, '..', 'js', 't20-atributos-resumo.js'));

// --- MB: sem conversão ---
const valores = helper.normalizarValoresResumoAtributos({ for: 18, des: 0, con: -1, int: 12, sab: 5, car: 8 }, { fallback: 10 });

assert.deepStrictEqual(valores, {
  for: '18',
  des: '0',
  con: '-1',
  int: '12',
  sab: '5',
  car: '8',
});

const vazio = helper.normalizarValoresResumoAtributos({ for: '', des: null }, { fallback: 0 });
assert.deepStrictEqual(vazio, {
  for: '0',
  des: '0',
  con: '0',
  int: '0',
  sab: '0',
  car: '0',
});

// --- v1.3: exibe valor nativo na ficha (For 5, Des 2, Int −1…) ---
const v13 = helper.normalizarValoresResumoAtributos(
  { for: 5, des: 3, con: 2, int: -1, sab: 0, car: -2 },
  { fallback: 0 }
);
assert.deepStrictEqual(v13, {
  for: '5',
  des: '3',
  con: '2',
  int: '-1',
  sab: '0',
  car: '-2',
});

const v13criacao = helper.normalizarValoresResumoAtributos(
  { for: 2, des: 1, con: 0, int: 0, sab: 3, car: 0 },
  { fallback: 0 }
);
assert.deepStrictEqual(v13criacao, {
  for: '2',
  des: '1',
  con: '0',
  int: '0',
  sab: '3',
  car: '0',
});

// v13Score legado: só wizard 4d6 (conversão opcional)
const v13score = helper.normalizarValoresResumoAtributos(
  { for: 2, des: 1, con: 0, int: 0, sab: 3, car: 0 },
  { fallback: 0, v13Score: true }
);
assert.deepStrictEqual(v13score, {
  for: '14',
  des: '12',
  con: '10',
  int: '10',
  sab: '16',
  car: '10',
});

console.log('t20-atributos-resumo regression test passed');
