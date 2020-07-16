#!/usr/bin/env python3
import sys


def generate_tmr_lib(fname_in, fname_out):
    """ This functions load standard library (from the PDK comonly used in HEP comunity) 
        from fname_in and writes simplified version to fname_out. The simplified version 
        contains only input/output declarations and it is meant to be used with TMRG flow.
    """
    ignore_module = False
    with open(fname_in) as fin:
        with open(fname_out, "w") as fout:
            for line in fin.readlines():
                line_striped = line.lstrip()
                if line_striped.startswith("module"):
                    ignore_module = bool(line_striped.find("BHD") > 0)
                    if not ignore_module:
                        fout.write(line)
                        if line_striped.find(" CKLH") > 0 or \
                           line_striped.find(" CKLN") > 0 or \
                           line_striped.find(" DF") > 0 or \
                           line_striped.find(" EDF") > 0 or \
                           line_striped.find(" SDF") > 0 or \
                           line_striped.find(" SEDF") > 0 or \
                           line_striped.find(" GDF") > 0 or \
                           line_striped.find(" GSDF") > 0:
                            fout.write("    // tmrg seu_reset CDN\n")
                            fout.write("    // tmrg seu_set   SDN\n")
                elif line_striped.startswith("input") or \
                        line_striped.startswith("output") or \
                        line_striped.startswith("endmodule"):
                    if not ignore_module:
                        fout.write(line)
                elif line_striped.startswith("primitive "):
                    break

def main():
    if len(sys.argv) != 3:
        print("Usage: %s mylib.v mylib_tmr.v" % (sys.argv[0]))
        sys.exit(-1)
    generate_tmr_lib(fname_in=sys.argv[1], fname_out=sys.argv[2])

if __name__ == "__main__":
    main()
