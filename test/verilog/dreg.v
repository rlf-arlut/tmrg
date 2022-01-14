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

module dreg (input clock,
             input d_reg,
             output reg q_reg);

  always @(posedge clock)
    q_reg <= d_reg;
endmodule
