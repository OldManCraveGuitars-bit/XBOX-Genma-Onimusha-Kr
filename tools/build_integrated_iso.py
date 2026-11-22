"""Assemble the v0.801 ISO from verified v0.8 content and the verified XBE.

This maintainer tool needs both local ISOs. End users need only the Japanese
original ISO and the published Windows patcher; the delta includes this step.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from build_hdd_text_fix import build, FIXED
from disc import Disc

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '7f5af784f9b229c5d0061918e018a9052e328a5341efc7d9e1b5d36de5f58206'
BASE = 'dbd207078fc41095afe805743277676214fc6e71d2cce2db30f0b161dc0f8dc2'
BLOCK = 8 * 1024 * 1024


def digests(path):
    hs = {name: hashlib.new(name) for name in ('md5', 'sha1', 'sha256')}
    with Path(path).open('rb') as f:
        while chunk := f.read(BLOCK):
            for h in hs.values():
                h.update(chunk)
    return dict(bytes=Path(path).stat().st_size, **{n: h.hexdigest() for n, h in hs.items()})


def entry(disc):
    return next(e for e in disc.entries if e['path'].casefold() == 'default.xbe')


def audit(base, target):
    before, after = Disc(base), Disc(target)
    try:
        old = {e['path']: e for e in before.entries}
        new = {e['path']: e for e in after.entries}
        assert old.keys() == new.keys(), 'ISO paths changed'
        changed = [p for p in old if old[p] != new[p]]
        assert changed == ['default.xbe'], changed
        a, b = entry(before), entry(after)
        assert a['table_entry_offset'] == b['table_entry_offset']
        assert b['offset'] == (before.length + 2047) & ~2047
        xbe = after.read(b['offset'], b['size'])
        assert hashlib.sha256(xbe).hexdigest() == FIXED
        assert struct.unpack_from('<I', xbe, 0x11c)[0] == 23
        allowed = a['table_entry_offset'] + 4
        pos = 0
        # Compare every byte of the base ISO; only the XBE directory extent moves.
        while pos < before.length:
            n = min(BLOCK, before.length - pos)
            left, right = bytearray(before.read(pos, n)), bytearray(after.read(pos, n))
            lo, hi = max(0, allowed - pos), min(n, allowed + 8 - pos)
            if lo < hi:
                left[lo:hi] = right[lo:hi] = bytes(hi - lo)
            assert left == right, f'Unexpected ISO changes at {pos:#x}'
            pos += n
        assert not any(after.read(before.length, b['offset'] - before.length))
        end = b['offset'] + b['size']
        assert after.length == (end + 2047) & ~2047
        assert not any(after.read(end, after.length - end))
        return dict(status='passed', entries=len(old), files=sum(not e['directory'] for e in old.values()),
                    changed_directory_entries=changed, all_other_iso_bytes_preserved=True,
                    unexpected_changed_bytes=0, integrated_xbe_sha256=FIXED,
                    integrated_xbe_bytes=len(xbe), integrated_xbe_sections=23,
                    external_xbe_replacement_required=False, physical_xbox_verified=False)
    finally:
        before.close()
        after.close()


def main():
    ap = argparse.ArgumentParser()
    for name in ('original-iso', 'base-iso', 'output'):
        ap.add_argument('--' + name, type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Output already exists'
    print('Validating Japanese original and v0.8 ISO hashes', flush=True)
    original_hashes, base_hashes = digests(args.original_iso), digests(args.base_iso)
    assert original_hashes['sha256'] == SOURCE and original_hashes['bytes'] == 4905566208
    assert base_hashes['sha256'] == BASE and base_hashes['bytes'] == 5385351168
    original, base = Disc(args.original_iso), Disc(args.base_iso)
    try:
        oe, be = entry(original), entry(base)
        fixed = build(original.read(oe['offset'], oe['size']), base.read(be['offset'], be['size']))
        record = be['table_entry_offset'] + 4
        offset = (base.length + 2047) & ~2047
        patch = struct.pack('<II', (offset - base.base) // 2048, len(fixed))
    finally:
        original.close()
        base.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    print('Writing the integrated ISO (all Korean content plus v0.801 XBE)', flush=True)
    created = False
    try:
        with args.base_iso.open('rb') as src, args.output.open('xb') as out:
            created = True
            pos = 0
            while chunk := src.read(BLOCK):
                buf = bytearray(chunk)
                lo, hi = max(pos, record), min(pos + len(buf), record + 8)
                if lo < hi:
                    buf[lo - pos:hi - pos] = patch[lo - record:hi - record]
                out.write(buf)
                pos += len(buf)
            out.write(bytes(offset - pos))
            out.write(fixed)
            out.write(bytes((-out.tell()) % 2048))
        print('Auditing every ISO byte and reading back the integrated XBE', flush=True)
        report = audit(args.base_iso, args.output)
        report.update(version='v0.801', source=original_hashes, base=base_hashes,
                      output=dict(name=args.output.name, **digests(args.output)))
        dest = ROOT / 'build/integrated-iso-v0.801.json'
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(json.dumps(report, indent=2) + '\n', 'utf8')
        print(json.dumps(report, indent=2), flush=True)
    except BaseException:
        # Only the new output created by this invocation is removed on failure.
        if created and args.output.exists():
            args.output.unlink()
        raise


if __name__ == '__main__':
    main()
