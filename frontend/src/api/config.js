export function resolverApiUrl({ runtimeUrl, buildUrl, development = false }) {
  const value = (runtimeUrl || buildUrl || (development ? 'http://localhost:8000' : '')).trim();
  if (!value) throw new Error('Configura API_URL en config.js antes de publicar el frontend.');
  const url = new URL(value);
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
    throw new Error('API_URL debe ser una URL HTTP(S) sin credenciales, query ni fragmento.');
  }
  if (!development && (url.protocol !== 'https:' || ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname))) {
    throw new Error('La API de producción debe usar HTTPS y un host público.');
  }
  return url.href.replace(/\/+$/, '');
}
