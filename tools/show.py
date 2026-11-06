# show.py <ghidra dir> <prog> addr[,addr..] [maxchars]: print cleaned decomp bodies
import sys,re,os
g,prog=sys.argv[1:3];want=[a.lower().zfill(8) for a in sys.argv[3].split(',')];mx=int(sys.argv[4]) if len(sys.argv)>4 else 700
txt=open(os.path.join(g,'decomp_%s.c'%prog),encoding='utf-8',errors='replace').read()
parts=re.split(r'// ==== (\S+) @ ([0-9a-f]+) size=(\d+)\n',txt)
for i in range(1,len(parts),4):
    a=parts[i+1].zfill(8)
    if a in want:
        b=parts[i+3]
        b=re.sub(r'/\*.*?\*/','',b,flags=re.S);b=re.sub(r'\n\s*\n','\n',b)
        b=re.sub(r'^\s*(undefined\d?|int|uint|short|ushort|byte|char|bool|code)\s*\*?\w+;\n','',b,flags=re.M)
        print('#####',a,parts[i],parts[i+2]);print(b[:mx])
