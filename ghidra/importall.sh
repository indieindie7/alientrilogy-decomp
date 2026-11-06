#!/bin/bash
cd $AT_ROOT/ghidra
for p in "IP.BIN 06002000" "PROG.BIN 06004000"; do bash import.sh $p; done > logs/import_all.txt 2>&1
echo done >> logs/import_all.txt
