// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the endmodule label which was discovered to
// cause issues. The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.28  mlupi   Created
//-----------------------------------------------------------------------------

module endmodule_label_dff(d,c,q);
  input d,c;
  output q;
  reg q;
  // tmrg default triplicate
  wire dVoted=d;
  always @(posedge c)
    q<=dVoted;
endmodule : endmodule_label_dff
