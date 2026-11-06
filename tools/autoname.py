# autoname.py <ghidra dir> <prog>: rule-based provisional names -> work/auto_<prog>.txt (hand-format lines). hand overrides applied later by merge.
import sys,os,re,json,collections
g,prog=sys.argv[1:3]
f=json.load(open(os.path.join(g,'work','feat_%s.json'%prog)))
txt=open(os.path.join(g,'decomp_%s.c'%prog),encoding='utf-8',errors='replace').read()
parts=re.split(r'// ==== (\S+) @ ([0-9a-f]+) size=(\d+)\n',txt)
body={}
for i in range(1,len(parts),4):
    b=re.sub(r'/\*.*?\*/','',parts[i+3],flags=re.S);body[parts[i+1].lower().zfill(8)]=b
areas=[l.split() for l in open(os.path.join(g,'work','areas_%s.txt'%prog)) if l.strip() and not l.startswith('#')]
areas=sorted((int(a,16),n) for a,n in areas)
def area(a):
    v=int(a,16);cur='sys'
    for s,n in areas:
        if s<=v: cur=n
        else: break
    return cur
hand0={}
_hp=os.path.join(g,'work','names_%s.txt'%prog)
if os.path.exists(_hp):
    for _l in open(_hp,encoding='utf-8'):
        _t=_l.split(' ',2)
        if len(_t)>1 and _l[0]!='#': hand0[int(_t[0],16)]=_t[1].split('_')[0]
_hk=sorted(hand0)
_skip={'sys','rtl','list','map','debug','gal','mth','cdc','heap','unpack'}
def area2(a):
    v=int(a,16);best=None
    for k in _hk:
        d=abs(k-v)
        if d<=0x180 and hand0[k] not in _skip and (best is None or d<best[0]): best=(d,hand0[k])
    return best[1] if best else area(a)
def role(a):
    x=f[a];b=body[a];n=x['size'];C=len(x['C'])
    sig=b.strip().split('\n')[0] if b.strip() else ''
    stm=b.count(';')
    params=len(re.findall(r'param_\d+',' '.join(set(re.findall(r'param_\d+',b)))))
    stores=len(re.findall(r'^\s*\*?[\w\[\]\(\)\*\+\s>-]*=[^=]',b,re.M))
    if 'unaff_gbr' in b: return 'GbrRegs'
    if 'in_vbr' in b or 'in_sr' in b or 'in_gbr' in b: return 'SysAsm'
    if re.search(r'jumptable|switch',b): 
        return 'StateDispatch' if C>=1 else 'Dispatch'
    if n<=8 and C==0 and not re.search(r'=',b): return 'Stub'
    if C==0 and re.search(r'\breturn\b\s*[-\w]+;',b) and stm<=3 and params==0 and '*' not in b.split('{',1)[-1]: return 'ReturnConst'
    if C==1 and stm<=4: return 'Thunk' if params==0 else 'Wrapper'
    loop=bool(re.search(r'\b(while|for|do)\b',b))
    if loop and C==0:
        if re.search(r'\*\w+ = \*\w+;',b) or re.search(r'\*\(\w+ \*\)\w+ = \*\(\w+ \*\)\w+;',b): return 'CopyLoop'
        if re.search(r'\*\w+ = (0|param_\d|\w+);\s*\n\s*\w+ = \w+ \+ 1',b): return 'FillLoop'
        return 'LoopCalc'
    if loop and C>=1: return 'ForEach'
    if re.search(r'(<< 0x?\w+|>> \w+)',b) and re.search(r' \* ',b) and C==0: return 'MathCalc'
    if C==0 and params==0 and stm<=2 and 'return' in b: return 'Get'
    if C==0 and stm<=3 and re.search(r'^\s*\*\(?[\w\s\*\)]*(DAT|PTR)_\w+\)? = param_1',b,re.M): return 'Set'
    if C==0 and params==0 and stores>=3: return 'InitVars'
    if C==0 and params>=1 and stores>=3: return 'SetupObj'
    if C==0 and stm<=6: return 'Access'
    if C>=10: return 'Run'
    if C>=1 and params==0 and stm>=3: return 'Tick'
    if C>=1 and len(re.findall(r'param_1 \+ 0x?\w+|\*\(\w+ \*\)\(param_1',b))>=3: return 'ObjProc'
    if C>=4: return 'Proc'
    if C==0: return 'Calc'
    return 'Step'
hand={}
hp=os.path.join(g,'work','names_%s.txt'%prog)
if os.path.exists(hp):
    for l in open(hp,encoding='utf-8'):
        l=l.rstrip('\n')
        if not l or l[0]=='#': continue
        t=l.split(' ',2); hand[t[0].lower().zfill(8)]=(t[1],t[2] if len(t)>2 else 'named from code/strings')
out=[];seen=collections.Counter()
for a in sorted(f):
    if a in hand: nm,desc=hand[a];tag='hand'
    else:
        r=role(a);ar=area2(a);x=f[a];nm='%s_%s_%s'%(ar,r,a[3:]);desc='structural name: %s near %s code, %d bytes, %d callees, %d callers'%(r,ar,x['size'],len(x['C']),len(x['callers']));tag='auto'
    seen[nm]+=1
    if seen[nm]>1: nm+='_%d'%seen[nm]
    out.append('0x%s func %s hand provisional %s'%(a,nm,desc))
open(os.path.join(g,'work','auto_%s.txt'%prog),'w').write('\n'.join(out)+'\n')
print(prog,len(out),'hand',len(hand),collections.Counter(role(a) for a in f if a not in hand).most_common())
