// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the case in which a signal contains reg
// in his name.
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.01.14  mlupi   Created
//-----------------------------------------------------------------------------

module dreg #(parameter N=2,
              parameter M=2)
  (input clock,
   input [N-1:0] d);

  reg [N-1:0] q [0:M-1];

  genvar i;
  generate
    for (i=0; i<M; i=i+1) begin
      always @(posedge clock)
        q[i] <= d;
    end
  endgenerate

endmodule
