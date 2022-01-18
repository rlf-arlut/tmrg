// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the case in which an unpacked array of
//  packed arrays is defined as module port (IEEE 1800-2017 section 23.2.2).
//  This testcase targets the case of unpacked array defined using
//  ranges in defition (IEEE 1800-2017 section 7.4.2).
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.01.14  mlupi   Created
//-----------------------------------------------------------------------------

module dreg #(parameter N=2,
              parameter M=2)
  (input clock,
   input [N-1:0] d [0:M-1]);

  reg [N-1:0] q [0:M-1];

  genvar i;
  generate
    for (i=0; i<M; i=i+1) begin
      always @(posedge clock)
        q[i] <= d[i];
    end
  endgenerate
endmodule
