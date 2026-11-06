// CreateAt.java: args are entry addresses (hex). Disassembles from each entry by flow and creates a DEFAULT function there
// with a flow-computed body (for orphan code no function owns). Prints the body size.
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;

public class CreateAt extends GhidraScript {
    @Override
    public void run() throws Exception {
        FunctionManager fm = currentProgram.getFunctionManager();
        for (String s : getScriptArgs()) {
            Address h = toAddr(Long.parseLong(s.replace("0x", ""), 16));
            if (fm.getFunctionAt(h) != null) { println("CreateAt: exists " + h); continue; }
            new DisassembleCommand(h, null, true).applyTo(currentProgram, monitor);
            CreateFunctionCmd c = new CreateFunctionCmd(null, h, null, ghidra.program.model.symbol.SourceType.DEFAULT);
            c.applyTo(currentProgram, monitor);
            Function n = fm.getFunctionAt(h);
            println("CreateAt: " + h + " " + (n == null ? "FAILED " + c.getStatusMsg() : "body=" + n.getBody().getNumAddresses() + " max=" + n.getBody().getMaxAddress()));
        }
    }
}
