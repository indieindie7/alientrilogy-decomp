# basefind.py <bin> : histogram of big-endian 32-bit words that look like Saturn RAM pointers, by 64 KB bucket.
import sys,struct,collections
b=open(sys.argv[1],'rb').read()
c=collections.Counter()
for i in range(0,len(b)-3,4):
    v=struct.unpack('>I',b[i:i+4])[0]
    if 0x06000000<=v<0x06100000 or 0x00200000<=v<0x00300000: c[v>>16<<16]+=1
tot=sum(c.values()); print(sys.argv[1], 'size',len(b),'ptrs',tot)
for k,n in sorted(c.items()): print('  %08x %6d'%(k,n))
