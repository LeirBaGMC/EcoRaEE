"""Genera un ZIP por lista permitida; nunca incluye .env reales ni datos locales."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    paths = sorted((ROOT / 'backend/app').rglob('*.py'))
    paths = [p for p in paths if '__pycache__' not in p.parts]
    paths += [ROOT / name for name in (
        'backend/scripts/__init__.py',
        'backend/scripts/validar_despliegue.py',
        'backend/scripts/crear_usuario.py',
        'backend/requirements.txt',
        'backend/ecoraee_cloud_sqlserver.sql',
        'backend/.env.aws.example',
        'deploy/ec2/ecoraee.service',
        'deploy/ec2/nginx.conf',
        'deploy/README.md',
    )]
    payloads = {}
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f'Archivo ausente o enlace no permitido: {path}')
        content = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
        if path.suffix == '.py':
            ast.parse(content, filename=str(path))
        payloads[path.relative_to(ROOT).as_posix()] = content.encode('utf-8')
    manifest = {name: hashlib.sha256(data).hexdigest()
                for name, data in payloads.items()}
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    archive = output / 'ecoraee-backend.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for name, data in payloads.items():
            bundle.writestr(name, data)
        bundle.writestr('MANIFEST.sha256.json', json.dumps(manifest, indent=2))
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise RuntimeError('ZIP corrupto')
        for name, digest in manifest.items():
            assert hashlib.sha256(bundle.read(name)).hexdigest() == digest
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / 'ecoraee-backend.zip.sha256').write_text(
        f'{digest}  {archive.name}\n', encoding='ascii')
    print(f'{archive}\n{len(payloads)} archivos + manifiesto; {archive.stat().st_size} bytes')
    print(f'SHA256: {digest}')


if __name__ == '__main__':
    main()
