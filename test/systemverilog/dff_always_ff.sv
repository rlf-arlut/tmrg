// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the always_ff acting like always in
//  sequential logic
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.28  mlupi   Created
//-----------------------------------------------------------------------------

module dff_always_ff
  (input logic d,
   input logic c,
   output logic q);
  // tmrg default triplicate
  wire dVoted=d;
  always_ff @(posedge c)
    q<=dVoted;
endmodule : dff_always_ff
