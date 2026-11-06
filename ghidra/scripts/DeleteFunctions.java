// DeleteFunctions.java: remove the functions whose entry addresses are given as arguments (hex, 0x prefix ok)
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class DeleteFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        int removed = 0;
        for (String a : args) {
            String s = a.startsWith("0x") ? a.substring(2) : a;
            Address addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(Long.parseLong(s, 16));
            Function f = currentProgram.getFunctionManager().getFunctionAt(addr);
            if (f == null) { println("DeleteFunctions: no function at " + addr); continue; }
            String name = f.getName();
            removeFunction(f);
            clearListing(f.getBody());
            removed++;
            println("DeleteFunctions: removed " + name + " at " + addr);
        }
        println("DeleteFunctions: removed " + removed + " of " + args.length + ", " + currentProgram.getFunctionManager().getFunctionCount() + " functions remain");
    }
}
