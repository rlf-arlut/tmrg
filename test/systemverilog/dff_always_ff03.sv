// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the always_ff acting like always in
//  sequential logic
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.02.02  mlupi   Created
//-----------------------------------------------------------------------------

module dff_always_ff03
  (input  logic d,
   input  logic rst,
   input  logic c,
   output logic q);

  // tmrg default triplicate
  wire dVoted=d;

  always_ff @(posedge c or posedge rst)
    if (rst) q <= 1'b0;
    else     q <=dVoted;

endmodule
