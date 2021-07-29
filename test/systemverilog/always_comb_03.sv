// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the always_comb construct.
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.29  mlupi   Created
//-----------------------------------------------------------------------------

module always_comb_03(in1,in2, out1);
  input in1,in2;
  output out1;
  always_comb
    out1 =  in1+in2;
endmodule // always_comb_03
