import re,csv
H={}
for l in open('../ghidra/hand_PROG.txt'):
    p=l.split()
    if len(p)>3: H[p[2]]=p[0][2:]
pred={l.split('\t')[0]:l.rstrip('\n').split('\t')[1] for l in open('tests.tsv')}
res={}
for l in open('out/results.tsv'):
    p=l.rstrip('\n').split('\t'); res[p[0]]=p
V,R,I,N='verified','refuted','inconclusive','renamed'
T={}
def g(v,obs,names,new=None):
    for n in names.split(): T[n]=(v,obs,new)
g(R,'no visible change in HUD/view/ammo (stub is not on the per-frame gameplay path, or draws only on change)','hud_Run_21b0c hud_Run_228d8 hud_ForEach_226e8 hud_ForEach_223f8 hud_ForEach_225b0 hud_ForEach_2239c hud_ForEach_22af4 hud_Tick_208fc hud_Tick_20990 hud_ForEach_20a10 hud_Tick_22ad0')
g(R,'only tiny frame diffs; HUD sprites/view intact, no stale sprites','hud_ClearSpriteTable')
g(R,'no visible change; gun, HUD, radar sprites all still drawn','vdp1_AppendCommand vdp1_SetCommandSlot gfx_AllocCommandBlock sprite_QueueEntry')
g(R,'no visible change, world still renders and input works','mesh_Run_1e1cc mesh_Run_1fa68 obj_Run_1b3f4 obj_Run_19ed4 rtl_Memcpy rtl_SignedDivide rtl_UnsignedDivide')
g(V,'3D view goes fully black from frame 0; HUD, fire (ammo 45->44) still work: stub removes world drawing','gfx_Step_0cec0')
g(V,'rendering glitch: stray diagonal line, distorted radar ring and weapon quad, ammo bar altered','mth_MacBlockProcess')
g(N,'world view black (HUD and fire still work): lookup feeds world rendering, no door/pickup effect seen','map_GetTileActionAt','map_LookupTileCell')
g(N,'view stops moving after arrow keys, radar sweep stops, fire still decrements ammo: global tick counter used for timing, not VDP1 draw','vdp1_SubmitCommandCounter','sys_CallAndIncTickCounter')
g(N,'ammo bar fill vanishes, number stays: draws ammo bar by mode (jump table 0-4, 0x20-byte quad)','obj_Run_1823c','hud_DrawAmmoBarByMode_1823c')
g(N,'health and ammo bars stop drawing: per-frame timer tick (not demo-only) that also calls two per-frame HUD updates','demo_TickTimers','game_TickFrameTimers')
g(V,'no change, as predicted (already empty / not used in gameplay)','sys_StubReturnVoidA sys_StubReturnVoidB rtl_Nop cd_LoadFile sfx_LoadTempBank backup_LoadSlotFromCard password_CheckEntered cpk_UpdatePlayback vdp1_ResetState vdp2_SetupScrollRegisters vdp1_SetFrameMode vdp1_SetEraseColorFromTable vdp1_SetSystemClip hud_DrawAutoMapperInventory heap_FindFreeBlock mesh_BuildVertexLists mesh_UploadVertices')
g(I,'no change, but state does not exercise it (no enemy in view / no steam / sound off); motion diff within noise','enemy_Run_10fac enemy_Run_12a80 enemy_Run_12e56 enemy_ForEach_1361e hazard_SteamValveStep snd_SendDriverCommand snd_SetMasterVolume mesh_MathCalc_0dee0')
rows=[l.split('\t')[0] for l in open('tests.tsv')]
assert set(rows)==set(T),(set(rows)^set(T))
md=['# Alien Trilogy control tests (11-06)','',
'Method: gameplay savestate (ctl/G0.mc0, level 1 corridor, health 100, ammo 45) loaded in mednafen headless; entry of each function patched to `000B 0009` (rts; nop), master cache disabled in the state (CCR=0, tags cleared); 1.5 s after load idle snap, 2.5 s later idle snap, Return (pad A = fire), then up 1.5 s + right 0.6 s. HUD/ammo/radar/view region diffs vs a baseline run of the same script (out/results.tsv, out/<name>/s0-3.png). Radar sweep and movement diffs carry timing noise, hp/ammo/view at idle are clean (0.0 in baseline).','',
'Driver: ctl/drv.py (ptest), ctl/ramtool.py, ctl/gen.py, ctl/tests.tsv.','',
'| addr | old name | prediction | patch | observation | verdict | new name |','|---|---|---|---|---|---|---|']
cnt={}
for n in rows:
    v,obs,new=T[n]; cnt[v]=cnt.get(v,0)+1
    r=res[n]; m=re.findall(r'(?:hp|ammo|view)=([\d.]+)',r[3].split(' | ')[0])
    md.append('| 0x%s | %s | %s | 000B0009 at entry | %s (s0 hp/ammo/view diff %s) | %s | %s |'%(H[n],n,pred[n],obs,'/'.join(m),v,new or '-'))
md+=['','Counts: '+', '.join('%s %d'%kv for kv in cnt.items())+', tested %d.'%len(rows),'',
'Caveats: "verified" for no-change predictions only means the patched function is off the executed path of this state, as predicted. Structural names (hud_/enemy_/obj_/mesh_ + hex) refuted = the stub had no visible effect, role unproven, name left unchanged. Fire = pad A (mapped to Return).']
open('../control_tests.md','w').write('\n'.join(md)+'\n')
# names file

order=[]
for l in open('../ghidra/work/names_PROG.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    if not l: continue
    order.append(l)
idx={l.split()[0].lower().zfill(8):i for i,l in enumerate(order) if l[0]!='#'}
for n in rows:
    v,obs,new=T[n]; a=H[n].zfill(8)
    nm=new or n
    if a in idx: desc=order[idx[a]].split(' ',2)[2] if len(order[idx[a]].split(' ',2))>2 else ''
    else: desc=''
    desc=re.sub(r' \(ctl 11-06.*\)$','',desc)
    tag={V:'verified ctl 11-06',R:'refuted ctl 11-06 (stub no effect)',I:'inconclusive ctl 11-06',N:'renamed from %s, ctl 11-06: %s'%(n,obs.split(':')[0])}[v]
    line='%s %s %s (%s)'%(a,nm,desc,tag) if desc else '%s %s %s'%(a,nm,tag)
    if a in idx: order[idx[a]]=line
    else: order.append(line)
open('../ghidra/work/names_PROG.txt','w',encoding='utf-8').write('\n'.join(order)+'\n')
print(cnt)
