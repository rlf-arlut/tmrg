// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the logic keyword in module call list
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.28  mlupi   Created
//-----------------------------------------------------------------------------

module dff_logic_port
  (input logic d,
   input logic c,
   output logic q);
  // tmrg default triplicate
  logic dVoted=d;
  always @(posedge c)
    q<=dVoted;
endmodule
