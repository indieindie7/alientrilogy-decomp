"""drv.py <script>: launch mednafen hidden (bgrun desktop claude_bg), post keys, snapshots.
Script lines: launch <cue> | wait <s> | key <name> <hold_s> | snap | save | load | quit | state <slot>
"""
import ctypes, ctypes.wintypes as W, subprocess, sys, time, os
u32 = ctypes.WinDLL('user32', use_last_error=True)
BG = r'C:\Users\john\Documents\Tools\mednafen\bgrun.py'
EXE = r'C:\Users\john\Documents\Tools\mednafen\mednafen.exe'
# name -> (windows scancode, extended)
SC = dict(up=0x11, left=0x1E, down=0x1F, right=0x20, start=0x1C, a=0x24, b=0x25, c=0x26, x=0x16, y=0x17, z=0x18,
          f5=0x3F, f7=0x41, f9=0x43, f8=0x42, f6=0x40, f10=0x44, f12=0x58, f11=0x57, k0=0x0B, k1=0x02, k2=0x03, k3=0x04, k4=0x05)
VK = dict(up=0x57, left=0x41, down=0x53, right=0x44, start=0x0D, a=0x4A, b=0x4B, c=0x4C, x=0x55, y=0x49, z=0x4F,
          f5=0x74, f7=0x76, f9=0x78, f8=0x77, f6=0x75, f10=0x79, f12=0x7B, f11=0x7A, k0=0x30, k1=0x31, k2=0x32, k3=0x33, k4=0x34)
EXTRA = []
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
hdesk = None; hwnd = None; pid = None
WNDENUM = ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)

import ctypes.wintypes as W2
k32 = ctypes.WinDLL('kernel32', use_last_error=True)
class SI(ctypes.Structure):
    _fields_ = [('cb', W.DWORD), ('lpReserved', W.LPWSTR), ('lpDesktop', W.LPWSTR), ('lpTitle', W.LPWSTR),
                ('dwX', W.DWORD), ('dwY', W.DWORD), ('dwXSize', W.DWORD), ('dwYSize', W.DWORD),
                ('dwXCountChars', W.DWORD), ('dwYCountChars', W.DWORD), ('dwFillAttribute', W.DWORD),
                ('dwFlags', W.DWORD), ('wShowWindow', W.WORD), ('cbReserved2', W.WORD),
                ('lpReserved2', ctypes.c_void_p), ('hStdInput', W.HANDLE), ('hStdOutput', W.HANDLE), ('hStdError', W.HANDLE)]
class PI(ctypes.Structure):
    _fields_ = [('hProcess', W.HANDLE), ('hThread', W.HANDLE), ('dwProcessId', W.DWORD), ('dwThreadId', W.DWORD)]
u32.CreateDesktopW.restype = W.HANDLE
def spawn(argv):
    global hdesk
    hdesk = u32.CreateDesktopW('claude_bg', None, None, 0, 0x10000000, None)
    si = SI(); si.cb = ctypes.sizeof(SI); si.lpDesktop = 'claude_bg'; si.dwFlags = 1; si.wShowWindow = 7
    pi = PI()
    if not k32.CreateProcessW(None, ctypes.create_unicode_buffer(subprocess.list2cmdline(argv)), None, None, False, 0x08000000, None, os.path.dirname(EXE), ctypes.byref(si), ctypes.byref(pi)):
        sys.exit('CreateProcess failed %d' % ctypes.get_last_error())
    return pi.dwProcessId
def find():
    res = []
    def cb(h, l):
        p = W.DWORD(); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid and u32.GetParent(h) == 0:
            cc = ctypes.create_unicode_buffer(50); u32.GetClassNameW(h, cc, 50)
            if cc.value == 'SDL_app': res.append((h, 1))
        return True
    u32.EnumDesktopWindows(hdesk, WNDENUM(cb), 0)
    # pick biggest-titled
    return max(res, key=lambda r: r[1])[0] if res else None
EXT = set()
def post(msg, name, up=False):
    sc = SC[name]; lp = 1 | (sc << 16)
    if name in EXT: lp |= (1 << 24)
    if up: lp |= (1 << 30) | (1 << 31)
    u32.PostMessageW(hwnd, msg, VK[name], lp)
def key(name, hold):
    post(0x100, name); time.sleep(hold); post(0x101, name, True)
import glob
from PIL import Image, ImageChops, ImageStat
def newest():
    return max(glob.glob(r'C:/Users/john/.mednafen/snaps/*.png'), key=os.path.getmtime)
def region(im, which):
    w, h = im.size
    return im.crop((0, int(h*0.88), w, h)) if which == 'bot' else im.crop((0, 0, w, int(h*0.1)))
def match(tpl, thr=2.0):
    time.sleep(0)
    key('f9', 0.1); time.sleep(0.8)
    t = Image.open(tpl).convert('L')
    im = region(Image.open(newest()), 'bot' if 'press' in tpl else 'top').convert('L').resize(t.size)
    d = ImageStat.Stat(ImageChops.difference(im, t)).mean[0]
    return d < thr, d
def run(path):
    global pid, hwnd
    for ln in open(path):
        t = ln.split('#')[0].split()
        if not t: continue
        c = t[0]
        if c == 'launch':
            pid = spawn([EXE, '-sound', '0', '-video.fs', '0', '-video.glvsync', '0', '-video.blit_timesync', '1'] + EXTRA + [ln.split('#')[0].strip()[7:]]); time.sleep(4)
            hwnd = find(); u32.PostMessageW(hwnd,0x1C,1,0); u32.PostMessageW(hwnd,0x6,1,0); u32.PostMessageW(hwnd,0x7,0,0); print('pid', pid, 'hwnd', hwnd, flush=True)
        elif c == 'raw':
            SC['_r']=int(t[1],16); VK['_r']=int(t[2],16)
            EXT.discard('_r')
            if len(t) > 4 and t[4] == 'ext': EXT.add('_r')
            key('_r', float(t[3]) if len(t) > 3 else 0.3)
        elif c == 'until':
            # until <tpl> <key|-> <maxtries>: press key (if not -) while not matching
            for n in range(int(t[3])):
                ok, d = match(t[1])
                if ok: print('matched', t[1], n, round(d, 1), flush=True); break
                if t[2] != '-': key(t[2], 0.2)
                time.sleep(2.5)
            else: print('NOMATCH', t[1], flush=True)
        elif c == 'opt': EXTRA.extend([t[1], ' '.join(t[2:])])
        elif c == 'wait': time.sleep(float(t[1]))
        elif c == 'key': key(t[1], float(t[2]) if len(t) > 2 else 0.1)
        elif c == 'snap': key('f9', 0.1); time.sleep(0.5)
        elif c == 'save': key('f5', 0.1); time.sleep(1)
        elif c == 'load': key('f7', 0.1); time.sleep(1)
        elif c == 'quit':
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True)
        elif c == 'dump':
            def cb2(w, l):
                p = W.DWORD(); u32.GetWindowThreadProcessId(w, ctypes.byref(p)); b = ctypes.create_unicode_buffer(100); u32.GetWindowTextW(w, b, 100)
                cc = ctypes.create_unicode_buffer(100); u32.GetClassNameW(w, cc, 100); print(w, p.value, repr(b.value), cc.value, u32.IsWindowVisible(w)); return True
            u32.EnumDesktopWindows(hdesk, WNDENUM(cb2), 0)
        elif c == 'ptest':
            import ramtool as rt, shutil
            name=t[1]; d=rt.load(os.path.join(HERE,'G0.mc0'))
            for sp in t[2:]:
                a,h=sp.split(':'); rt.wr(d,int(a,16),bytes.fromhex(h))
            d[223591]=0
            for i in range(218359,218359+1024): d[i]=0
            rt.save(d,rt.MC); time.sleep(0.3)
            key('f7',0.1); time.sleep(1.5)
            fs=[]
            def sn():
                key('f9',0.1); time.sleep(0.7); fs.append(newest())
            sn(); time.sleep(2.5); sn()
            SC['_r']=0x1C; VK['_r']=0x0D; EXT.discard('_r'); key('_r',0.4); time.sleep(0.5); sn()
            SC['_r']=0x48; VK['_r']=0x26; EXT.add('_r'); key('_r',1.5); SC['_r']=0x4D; VK['_r']=0x27; key('_r',0.6)
            time.sleep(0.5); sn()
            key('f5',0.1); time.sleep(1.2)
            os.makedirs(os.path.join(HERE,'out',name),exist_ok=True)
            shutil.copy(rt.MC, os.path.join(HERE,'out',name+'.mc0'))
            for k,f in enumerate(fs): shutil.copy(f, os.path.join(HERE,'out',name,'s%d.png'%k))
            bd=os.path.join(HERE,'out','base')
            R=dict(hp=(210,10,312,50),ammo=(15,203,145,225),radar=(225,150,320,235),view=(0,0,205,200))
            res=[]
            for k in range(4):
                a=Image.open(os.path.join(HERE,'out',name,'s%d.png'%k)).convert('L')
                if os.path.exists(os.path.join(bd,'s%d.png'%k)):
                    b=Image.open(os.path.join(bd,'s%d.png'%k)).convert('L')
                    res.append(' '.join('%s=%.1f'%(rn,ImageStat.Stat(ImageChops.difference(a.crop(rg),b.crop(rg))).mean[0]) for rn,rg in R.items()))
            ims=[Image.open(f).convert('L') for f in fs]
            dab=ImageStat.Stat(ImageChops.difference(ims[0],ims[1])).mean[0]
            dbc=ImageStat.Stat(ImageChops.difference(ims[1],ims[3])).mean[0]
            open(os.path.join(HERE,'out','results.tsv'),'a').write(name+chr(9)+' '.join(t[2:])+chr(9)+'idle%.2f mv%.2f'%(dab,dbc)+chr(9)+' | '.join(res)+chr(10))
            print('done',name,round(dab,2),round(dbc,2),res,flush=True)
        elif c == 'pid': print(pid)
if __name__ == '__main__': run(sys.argv[1])
