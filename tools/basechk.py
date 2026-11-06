# basechk.py <bin> <lo> <hi> <step> : score candidate bases by pointers landing on SH-2 prologues (sts.l pr / mov.l r14,@-r15 / add #-n,r15)
import sys,struct
b=open(sys.argv[1],'rb').read(); lo,hi,st=(int(x,0) for x in sys.argv[2:5])
ptrs=[struct.unpack('>I',b[i:i+4])[0] for i in range(0,len(b)-3,4)]
ptrs=[v for v in ptrs if 0x06000000<=v<0x06100000 or 0x00200000<=v<0x00300000]
def pro(o): 
    if o<0 or o+2>len(b): return False
    w=b[o:o+2]; return w in (b'\x4f\x22',b'\x2f\xe6',b'\x2f\xd6',b'\x2f\xc6',b'\x2f\x86') or (w[0]==0x7f)
res=[]
for base in range(lo,hi,st):
    hit=0; ins=0; ents=set()
    for v in ptrs:
        o=v-base
        if 0<=o<len(b):
            ins+=1
            if (o&1)==0 and pro(o): hit+=1; ents.add(o)
    res.append((len(ents),hit,ins,base))
for e,h,i,base in sorted(res,reverse=True)[:6]: print('%08x entries %d hits %d inside %d'%(base,e,h,i))
