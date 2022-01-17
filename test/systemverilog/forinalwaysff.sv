// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the case in which a for is contained in an
//  always block
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.01.14  mlupi   Created
//-----------------------------------------------------------------------------

module dreg #(parameter N=2)
  (input clock,
   input [N-1:0] d,
   output reg [N-1:0] q);

  always_ff @(posedge clock)
    for (int i=0; i<N; i++)
      q[i] <= d[N-i];
endmodule