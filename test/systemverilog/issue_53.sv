// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to reproduce #53
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.02.14  mlupi   Created
//-----------------------------------------------------------------------------

module test;
  import mypkg::A;
  localparam B = A;
  import mypkg::C;
  localparam D = C;
endmodule
