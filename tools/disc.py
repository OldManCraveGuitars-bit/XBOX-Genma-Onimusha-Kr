"""Checked, read-only XDVDFS reader for the user-supplied Xbox disc."""
from pathlib import Path, PurePosixPath
import hashlib
import struct

MAGIC = b'MICROSOFT*XBOX*MEDIA'


class Disc:
    def __init__(self, path):
        self.path = Path(path)
        self.length = self.path.stat().st_size
        self.f = self.path.open('rb')
        for base in (0, 0x18300000, 0xFD90000, 0x2080000):
            self.f.seek(base + 0x10000)
            descriptor = self.f.read(2048)
            if descriptor[:20] == MAGIC and descriptor[-20:] == MAGIC:
                self.base, self.descriptor = base, descriptor
                sector, size = struct.unpack_from('<II', descriptor, 20)
                break
        else:
            self.f.close()
            raise ValueError('XDVDFS volume descriptor not found')
        self.entries = []
        self._directories = set()
        self._paths = set()
        self._walk('', sector, size)

    def read(self, offset, size):
        if offset < 0 or size < 0 or offset + size > self.length:
            raise ValueError('Disc extent outside ISO')
        self.f.seek(offset)
        data = self.f.read(size)
        if len(data) != size:
            raise EOFError(offset)
        return data

    def _walk(self, parent, sector, size):
        if not size:
            return
        if (sector, size) in self._directories:
            raise ValueError('Directory cycle')
        self._directories.add((sector, size))
        data = self.read(self.base + sector * 2048, size)
        if data[:14] == b'\xff' * 14 or data[:14] == b'\0' * 14:
            return
        visited = set()

        def node(offset):
            if offset in visited or offset + 14 > size:
                raise ValueError(f'Invalid directory node: {parent}:{offset}')
            visited.add(offset)
            left, right, start, length, attrs, nlen = struct.unpack_from('<HHIIBB', data, offset)
            if offset + 14 + nlen > size:
                raise ValueError('Truncated directory name')
            name = data[offset + 14:offset + 14 + nlen].decode('ascii')
            if not name or name in ('.', '..') or any(c in name for c in '/\\:\x00'):
                raise ValueError('Unsafe disc path')
            path = (PurePosixPath(parent) / name).as_posix()
            if left:
                node(left * 4)
            if path.casefold() in self._paths:
                raise ValueError('Duplicate disc path')
            self._paths.add(path.casefold())
            offset_on_disc = self.base + start * 2048
            if offset_on_disc + length > self.length:
                raise ValueError('Invalid file extent')
            entry = dict(path=path, sector=start, offset=offset_on_disc, size=length,
                         directory=bool(attrs & 0x10),
                         table_entry_offset=self.base + sector * 2048 + offset)
            self.entries.append(entry)
            if entry['directory']:
                self._walk(path, start, length)
            if right:
                node(right * 4)
        node(0)

    def extract(self, dest, log=print):
        dest = Path(dest).resolve()
        hashes = {}
        for e in self.entries:
            if e['directory']:
                continue
            target = dest.joinpath(*PurePosixPath(e['path']).parts).resolve()
            if not target.is_relative_to(dest):
                raise ValueError('Extraction escapes destination')
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            self.f.seek(e['offset'])
            remaining = e['size']
            with target.open('wb') as out:
                while remaining:
                    block = self.f.read(min(4 * 1024 * 1024, remaining))
                    if not block:
                        raise EOFError(e['path'])
                    out.write(block)
                    digest.update(block)
                    remaining -= len(block)
            hashes[e['path']] = digest.hexdigest()
            log(f"{e['size']:12d} {e['path']}")
        return hashes

    def close(self):
        self.f.close()
