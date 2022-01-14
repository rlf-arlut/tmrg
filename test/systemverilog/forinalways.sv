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

module comb #(parameter N=2)
  (input [N-1:0] d,
   output reg [N-1:0] q);

  always @(d)
    for (int i=0; i<N; i++)
      q[i] <= d[N-i];
endmodule
