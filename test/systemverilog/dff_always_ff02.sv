// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the always_ff acting like always in
//  sequential logic
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.28  mlupi   Created
//-----------------------------------------------------------------------------

module dff_always_ff02
  (input  logic d,
   input  logic rst,
   input  logic c,
   output logic q);

  // tmrg default triplicate
  wire dVoted=d;

  always_ff @(posedge c)
    if (rst) q <= 1'b0;
    else     q <=d Voted;

endmodule
