# Alien Trilogy (Sega Saturn, USA, Probe / Acclaim 1996) reverse-engineering names

Function names for the Saturn port of **Alien Trilogy** (disc id T-8113H V1.000, 1996-07-20). Both SH-2 programs on the disc are
loaded as raw images and every function carries a name (0 `FUN_` placeholders left). No public decomp of this game existed when this was started (web check 2026-11-06).

| Program (disc file) | Load base | Functions | `provisional` |
|---|---|---|---|
| IP.BIN (boot code, sectors 0-1) | 0x06002000 | 6 | 6 |
| 1111US.BIN (main game, first-read file) | 0x06004000 | 1,143 | 1,143 |
| **Total** | | **1,149** | **1,149** |

IP.BIN header: first-read address 0x06004000 (size 0, so the first root-directory file `1111US.BIN`, 349,768 bytes). Base 0x06004000 scored 983 prologue-matching pointer targets with `tools/basechk.py` (next best 91).
Skipped as data / 68k: `TWEPSG.BIN`, `TWEPSM.BIN`, `SFX/*`, `CPK/SDDRV.TSK` (SCSP sound driver), `*.BND`, `*.MAP`, `*.CPK`.

**Names are heuristic and all provisional.** 123 names were written from reading the decompile (strings, hardware registers, SDK-style helper shape):
backup RAM, CD loading, Cinepak (`cpk_`), SMPC, VDP1/VDP2, SCU, CD block (`cdc_`), libc-style helpers (`rtl_`), software divide. The other 1,026 are
structural names `<area>_<Role>_<addr>` (role from body shape: Thunk, Wrapper, CopyLoop, FillLoop, ObjProc, Tick, Step...; area from the nearest hand-named neighbour or the address map in `ghidra/naming/areas_PROG.txt`).
Area labels are guesses by address neighbourhood; treat them as placeholders until the function is read.

**No game data is included**: no disc image, executables, decompiled C or game text (string lines are stripped from the funcinfo exports).

## Layout
| Path | Content |
|---|---|
| `ghidra/hand_<PROG>.txt` | `0x<addr> func <name> hand provisional <comment>` (ApplyNames.java, hand mode) |
| `ghidra/funcinfo_<PROG>.tsv` | per-function export: `F` address name source size, `C` callees |
| `ghidra/naming/` | hand-written names (`names_PROG.txt`) and the area map used by the structural namer |
| `ghidra/scripts/` | FindSh2FunctionsMem, CreateAt, ApplyNames, ExportFuncInfo, CsDumpAll and helpers |
| `tools/` | basechk/basefind (load bases), feat.py (per-function features), autoname.py (structural names), show.py |

## Reproduce
1. Extract track 1 of your own disc dump (raw 2352-byte sectors) into a folder; copy `1111US.BIN` to `ghidra/bin/PROG.BIN`, and IP.BIN = user data of sectors 0-1 (first 3,852 bytes) to `ghidra/bin/IP.BIN`.
2. `tools/basechk.py` confirms the bases; import as raw binary, language `SuperH:BE:32:SH-2`, bases from the table (`ghidra/import.sh`, `importall.sh`; set `AT_ROOT` / `AT_WIN` to your paths).
3. `ghidra/apply.sh PROG` regenerates structural names (`tools/feat.py` then `tools/autoname.py`), applies them and re-exports; `IP` applies `hand_IP.txt` directly.

Non-commercial study and preservation. Notes, names and tools: MIT (`LICENSE`). Alien Trilogy belongs to its rights holders.
