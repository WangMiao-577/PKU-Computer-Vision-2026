#!/usr/bin/env python3
"""Restore archived large files offline, checking every SHA-256 before replacement."""
from pathlib import Path
import argparse, hashlib, json, os, tempfile

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024), b''): h.update(block)
    return h.hexdigest()

def restore(root, verify_only=False):
    root=root.resolve()
    manifest=json.loads((root/'LargeFiles/manifest.json').read_text())
    for item in manifest['files']:
        target=(root/item['path']).resolve()
        if not target.is_relative_to(root): raise ValueError('Unsafe target path')
        for part in item['parts']:
            p=(root/part['path']).resolve()
            if not p.is_relative_to(root): raise ValueError('Unsafe part path')
            if p.stat().st_size != part['bytes'] or digest(p)!=part['sha256']:
                raise ValueError('Invalid part: '+part['path'])
        if target.exists():
            if target.stat().st_size!=item['bytes'] or digest(target)!=item['sha256']:
                raise ValueError('Existing file differs; refusing overwrite: '+item['path'])
            print('Verified existing:', item['path'])
            continue
        if verify_only:
            h=hashlib.sha256();size=0
            for part in item['parts']:
                with (root/part['path']).open('rb') as f:
                    for block in iter(lambda:f.read(4*1024*1024),b''):
                        h.update(block);size+=len(block)
            if size!=item['bytes'] or h.hexdigest()!=item['sha256']: raise ValueError('Combined checksum mismatch')
            print('Verified parts:',item['path'])
            continue
        target.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix='.restore-',dir=target.parent)
        temp=Path(tmp)
        try:
            h=hashlib.sha256();size=0
            with os.fdopen(fd,'wb') as out:
                for part in item['parts']:
                    with (root/part['path']).open('rb') as f:
                        for block in iter(lambda:f.read(4*1024*1024),b''):
                            h.update(block);out.write(block);size+=len(block)
            if size!=item['bytes'] or h.hexdigest()!=item['sha256']:raise ValueError('Combined checksum mismatch')
            temp.replace(target)
            print('Restored:',item['path'])
        finally:
            if temp.exists():temp.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify',action='store_true',help='Only verify; write no files')
    args=parser.parse_args()
    restore(Path(__file__).resolve().parents[1],args.verify)
