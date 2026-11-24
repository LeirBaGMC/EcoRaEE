import test from 'node:test';
import assert from 'node:assert/strict';
import { resolverApiUrl } from '../src/api/config.js';

test('permite cambiar la API sin recompilar y normaliza la URL', () => {
  assert.equal(resolverApiUrl({ runtimeUrl: 'https://api.cloudfront.net/', buildUrl: 'https://anterior.example' }), 'https://api.cloudfront.net');
});
test('producción no cae silenciosamente en localhost o HTTP', () => {
  for (const runtimeUrl of ['', 'http://api.example', 'https://localhost', 'https://user:pass@api.example', 'https://api.example?token=x']) {
    assert.throws(() => resolverApiUrl({ runtimeUrl }));
  }
});
test('desarrollo conserva el backend local', () => {
  assert.equal(resolverApiUrl({ development: true }), 'http://localhost:8000');
});
