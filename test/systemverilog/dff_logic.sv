// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the logic construct replacing reg/wire
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.28  mlupi   Created
//-----------------------------------------------------------------------------

module dff_logic(d,c,q);
  // tmrg default triplicate
  input d,c;
  output q;
  logic q;
  logic dVoted=d;
  always @(posedge c)
    q<=dVoted;
endmodule
