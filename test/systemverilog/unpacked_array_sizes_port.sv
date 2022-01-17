// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the case of unpacked array defined using
//  sizes in defition (IEEE 1800-2017 section 7.4.2) and used in the ports of
//  of a module (IEEE 1800-2017 section 23.2.2).
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.01.14  mlupi   Created
//-----------------------------------------------------------------------------

module mymod #(parameter M=2)
  (input  logic clock,
   input  logic [M-1:0] d,
   output logic q [M]);
endmodule