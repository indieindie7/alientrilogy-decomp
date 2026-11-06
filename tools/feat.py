# feat.py <ghidra dir> <prog> <base hex>: per-function features -> work/feat_<prog>.json
import sys,os,re,json,struct,collections
g,prog,base=sys.argv[1],sys.argv[2],int(sys.argv[3],16)
b=open(os.path.join(g,'bin',prog+'.BIN'),'rb').read()
def dw(a):
    o=a-base
    return struct.unpack('>I',b[o:o+4])[0] if 0<=o<=len(b)-4 else None
def reg(v):
    if v is None: return None
    t=[(0x25C00000,0x25C80000,'vdp1vram'),(0x25D00000,0x25D00100,'vdp1reg'),(0x25E00000,0x25F00000,'vdp2vram'),(0x25F00000,0x25F80000,'vdp2cram'),(0x25F80000,0x25F81000,'vdp2reg'),
       (0x25FE0000,0x25FF0000,'scu'),(0x20100000,0x20100100,'smpc'),(0x25A00000,0x25B00000,'scspram'),(0x25B00000,0x25B01000,'scspreg'),(0x25800000,0x25900000,'cdblock'),
       (0xFFFFFE00,0xFFFFFFFF,'sh2reg'),(0x20000000,0x20100000,'rom'),(0x00200000,0x00300000,'lowram'),(0x06000000,0x06100000,'hiram'),(0x05800000,0x05900000,'cdblk'),(0x25000000,0x25800000,'bbus')]
    for lo,hi,n in t:
        if lo<=v<hi: return n
    return None
hdr=re.compile(r'// ==== (\S+) @ ([0-9a-fA-F]+) size=(\d+)')
funcs={};cur=None
for l in open(os.path.join(g,'decomp_%s.c'%prog),encoding='utf-8',errors='replace'):
    m=hdr.match(l)
    if m:
        cur=m.group(2).lower().zfill(8); funcs[cur]={'size':int(m.group(3)),'body':[]};continue
    if cur: funcs[cur]['body'].append(l)
info={};cur=None
for l in open(os.path.join(g,'funcinfo_%s.tsv'%prog),encoding='utf-8',errors='replace'):
    l=l.rstrip('\n');p=l.split(' ')
    if p[0]=='F': cur=p[1].lower().zfill(8); info[cur]={'C':[],'S':[]}
    elif p[0]=='C' and cur: info[cur]['C'].append(p[1].lower().zfill(8))
    elif p[0]=='S' and cur: info[cur]['S'].append(l[2:])
callers=collections.defaultdict(set)
for a,i in info.items():
    for c in i['C']: callers[c].add(a)
out={}
for a,f in funcs.items():
    body=''.join(f['body'])
    regs=collections.Counter();gl=set();lits=[]
    for m in re.finditer(r'\b(?:PTR_)?(?:DAT|PTR|s|u|PTR_DAT|PTR_s|PTR_FUN)_?(?:\w*?_)?([0-9a-f]{8})\b',body):
        pass
    for m in re.finditer(r'\b(PTR_\w+?|DAT)_([0-9a-f]{8})\b',body):
        v=dw(int(m.group(2),16))
        if v is None: continue
        r=reg(v)
        if r: regs[r]+=1
        if r in('hiram','lowram','bbus','vdp1vram','vdp1reg','vdp2reg','vdp2vram','vdp2cram','scu','smpc','scspreg','cdblock','sh2reg'): gl.add(v)
    sig=re.search(r'^[^\n/][^\n]*\(.*\)\s*$',body,re.M)
    out[a]={'size':f['size'],'regs':dict(regs),'gl':sorted(gl)[:12],'C':info.get(a,{}).get('C',[]),'S':info.get(a,{}).get('S',[]),
      'callers':sorted(callers.get(a,[])),'lines':body.count('\n'),'loop':int(bool(re.search(r'\b(for|while|do)\b',body))),'sig':sig.group(0)[:90] if sig else ''}
json.dump(out,open(os.path.join(g,'work','feat_%s.json'%prog),'w'))
print(prog,len(out))
