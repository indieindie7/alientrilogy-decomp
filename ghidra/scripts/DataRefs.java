// For each address argument list every reference to it: type, from address, containing function.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
public class DataRefs extends GhidraScript {
    public void run() throws Exception {
        for (String s : getScriptArgs()) {
            Address a = toAddr(Long.parseLong(s.replace("0x", ""), 16));
            for (Reference r : currentProgram.getReferenceManager().getReferencesTo(a)) {
                Function f = getFunctionContaining(r.getFromAddress());
                Instruction ins = currentProgram.getListing().getInstructionAt(r.getFromAddress());
                println("R " + a + " " + r.getReferenceType() + " " + r.getFromAddress() + " " + (f == null ? "-" : f.getName()) + " | " + (ins == null ? "-" : ins.toString()));
            }
        }
    }
}
