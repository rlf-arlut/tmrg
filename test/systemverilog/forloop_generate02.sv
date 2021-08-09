// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to test the generate construct in Systemverilog
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.08.09  mlupi   Created
//-----------------------------------------------------------------------------

module seq(
  input c,
  input r,
  output reg a
  );
  always @(posedge c)
    if (r) a <= 1'b0;
    else   a <= a + 1'b1;
endmodule

module forloop_generate_02
  (input logic c,
   input logic r,
   output logic [31:0] a);

  generate
    for (genvar j=0; j<32; j++) begin : gen_seq
      seq seq (
        .c(c),
        .r(r),
        .a(a[j])
      );
    end
  endgenerate
endmodule
