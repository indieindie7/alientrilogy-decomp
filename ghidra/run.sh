#!/bin/bash
# headless Ghidra on the Gungriffon project. usage: ckrun.sh <abs log> <args...> (e.g. -process X -noanalysis -postScript Y)
log="$1"; shift
cd $AT_ROOT/ghidra || exit 1
cmd //c "ghidra-headless.bat %AT_WIN%\ghidra AT $* -scriptPath ${SP:-%AT_WIN%\ghidra\scripts}" < /dev/null > "$log" 2>&1
tail -2 "$log"
