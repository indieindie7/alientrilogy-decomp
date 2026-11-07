import gzip,struct,sys,shutil,os
MC=os.path.expanduser("~/.mednafen/mcs/Alien Trilogy (USA).b096eb0829e98a8de92bda16d02f6a9c.mc0")
def load(p):
    return bytearray(gzip.open(p).read())
def find(d,name):
    b=name.encode(); i=d.find(bytes([len(b)])+b)
    return i
def hram_off(d): return 4408456
def rd(d,a,n):
    o=hram_off(d)+(a-0x06000000)
    out=bytearray(n)
    for k in range(n):
        x=(o+k)^1; out[k]=d[x]
    return bytes(out)
def wr(d,a,bs):
    o=hram_off(d)+(a-0x06000000)
    for k,v in enumerate(bs): d[(o+k)^1]=v
def save(d,p):
    with gzip.GzipFile(p,'wb',9) as f: f.write(bytes(d))
if __name__=="__main__":
    d=load(sys.argv[1])
    for n in ("Cache->Tag","Cache->Data","CCR"):
        i=find(d,n); print(n,i, d[i:i+40] if i>=0 else None)
    print(rd(d,0x06004000,16).hex())
