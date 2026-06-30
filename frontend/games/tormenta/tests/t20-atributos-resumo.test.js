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

// --- v1.3: score d20 = 10 + 2×attr ---
// for=2 → 14, des=1 → 12, con=5 → 20, int=0 → 10, sab=3 → 16, car=0 → 10
const v13 = helper.normalizarValoresResumoAtributos(
  { for: 2, des: 1, con: 5, int: 0, sab: 3, car: 0 },
  { fallback: 0, v13Score: true }
);
assert.deepStrictEqual(v13, {
  for: '14',
  des: '12',
  con: '20',
  int: '10',
  sab: '16',
  car: '10',
});

// Atributos negativos: -1 → 8, -2 → 6
const v13neg = helper.normalizarValoresResumoAtributos(
  { for: -2, des: -1, con: 0, int: 0, sab: 0, car: 0 },
  { fallback: 0, v13Score: true }
);
assert.deepStrictEqual(v13neg, {
  for: '6',
  des: '8',
  con: '10',
  int: '10',
  sab: '10',
  car: '10',
});

// Fallback v1.3 (valor ausente): fallback nativo 0 → score 10
const v13fback = helper.normalizarValoresResumoAtributos({}, { fallback: 0, v13Score: true });
assert.deepStrictEqual(v13fback, {
  for: '10',
  des: '10',
  con: '10',
  int: '10',
  sab: '10',
  car: '10',
});

console.log('t20-atributos-resumo regression test passed');
