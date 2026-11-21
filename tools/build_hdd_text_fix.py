"""Build the v0.8 Korean replacement XBE with the original 23-section layout.

Inputs are locally extracted XBEs from the exact supported original and v0.8
ISO. No game files are downloaded. Existing output files are never replaced.
"""
import argparse,hashlib,struct
from pathlib import Path

ORIGINAL='149f8392db82bbe092ce9b042310373e4645fa898624f57eea55a0c145885216'
V08='c6cad11380e0bdc8aa9eddc0e97748f589c681695ab745cbf6e79832babd16ad'
FIXED='81a65ca47a0e5d72944895a7b0aa0eee609689c1aa0896041ce3c1a95f45664c'

def build(original,translated):
    assert hashlib.sha256(original).hexdigest()==ORIGINAL,'Unsupported original XBE'
    assert hashlib.sha256(translated).hexdigest()==V08,'Unsupported v0.8 XBE'
    u32=lambda data,pos:struct.unpack_from('<I',data,pos)[0]
    base=u32(original,0x104);table=u32(original,0x120)-base
    assert u32(original,0x11c)==23 and u32(translated,0x11c)==24
    last=table+22*56;kr=table+23*56
    _,va,_,raw,raw_size=struct.unpack_from('<5I',original,last)
    _,kr_va,_,kr_raw,kr_size=struct.unpack_from('<5I',translated,kr)
    assert (va,raw,raw_size,kr_va)==(0x573380,0x23f000,0x2800,0x580000)
    data=bytearray(translated[:raw]);data[:0x1000]=original[:0x1000]
    data.extend(original[raw:raw+raw_size]);payload_at=raw+kr_va-va
    data.extend(bytes(payload_at-len(data)));data.extend(translated[kr_raw:kr_raw+kr_size])
    size=(kr_va+kr_size-va+3)&~3;data.extend(bytes(raw+size-len(data)))
    for pos,value in ((last,6),(last+8,size),(last+16,size),(0x10c,va+size-base),
                      (u32(data,0x118)-base+0x9c,0x800000ff)):
        struct.pack_into('<I',data,pos,value)
    for index in range(23):
        head=table+index*56;start,length=struct.unpack_from('<II',data,head+12)
        data[head+36:head+56]=hashlib.sha1(struct.pack('<I',length)+data[start:start+length]).digest()
    data.extend(bytes((-len(data))&4095))
    assert hashlib.sha256(data).hexdigest()==FIXED,'Generated XBE does not match verified replacement'
    return data

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--original-xbe',type=Path,required=True);ap.add_argument('--v08-xbe',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    data=build(args.original_xbe.read_bytes(),args.v08_xbe.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('xb') as output:output.write(data)
    print(FIXED+'  '+str(args.output))

if __name__=='__main__':main()
