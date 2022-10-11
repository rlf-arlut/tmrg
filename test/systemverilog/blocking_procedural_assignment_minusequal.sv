// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the blocking procedural assing in LRM
// IEEE1800-2009 Syntax 10-2.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.10.11  mlupi   Created
//-----------------------------------------------------------------------------

module bpa // Blocking procedural assign
  (output logic [9:0]   a,
   input  logic [479:0] b);

  // tmrg default triplicate
  always_comb begin
    a = '0;
    for (int k = 0; k <= 47; k++) begin
      a -= b[k*10+:10];
    end
  end
endmodule
