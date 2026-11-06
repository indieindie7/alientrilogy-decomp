#!/bin/bash
# usage: apply.sh <IP|PROG>: autoname -> hand file, apply names, re-export (funcinfo + decomp)
cd $AT_ROOT/ghidra
p=$1; G='%AT_WIN%\ghidra'; L=$AT_ROOT/ghidra/logs
if [ "$p" = PROG ]; then py -3.13 -I ../tools/autoname.py . PROG >/dev/null; cp work/auto_PROG.txt hand_PROG.txt; fi
bash run.sh $L/apply_$p.log -process $p.BIN -noanalysis -postScript ApplyNames.java "$G\hand_$p.txt" >/dev/null 2>&1
bash run.sh $L/export_$p.log -process $p.BIN -noanalysis -readOnly -postScript ExportFuncInfo.java "$G\funcinfo_$p.tsv" >/dev/null 2>&1
echo "$p FUN_ left: $(awk '$1=="F" && $3 ~ /^FUN_/' funcinfo_$p.tsv | wc -l) total $(awk '$1=="F"' funcinfo_$p.tsv | wc -l)"
