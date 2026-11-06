#!/bin/bash
# usage: import.sh <prog file name in bin/> <base>   (imports SH-2 BE at base, finds functions, exports funcinfo + decomp dump)
cd $AT_ROOT/ghidra
G='%AT_WIN%\ghidra'; L=$AT_ROOT/ghidra/logs
p=$1; base=$2; n=${p%.*}
bash run.sh $L/import_$n.log -import "$G\bin\\$p" -processor SuperH:BE:32:SH-2 -loader BinaryLoader -loader-baseAddr $base -postScript FindSh2FunctionsMem.java -postScript CreateAt.java $base >/dev/null 2>&1
bash run.sh $L/export_$n.log -process $p -noanalysis -readOnly -postScript ExportFuncInfo.java "$G\funcinfo_$n.tsv" >/dev/null 2>&1
bash run.sh $L/dump_$n.log -process $p -noanalysis -readOnly -postScript CsDumpAll.java "$G\decomp_$n.c" >/dev/null 2>&1
echo "$p F=$(awk '$1=="F"' funcinfo_$n.tsv 2>/dev/null | wc -l) dump=$(grep -c '^// ====' decomp_$n.c 2>/dev/null)"
