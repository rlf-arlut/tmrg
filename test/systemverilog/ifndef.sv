// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the ifndef construct wrapping a complete
//  module.
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.01.14  mlupi   Created
//-----------------------------------------------------------------------------

`ifdef MOD
`define MOD

module mymodule;
  reg d;
endmodule

`endif
