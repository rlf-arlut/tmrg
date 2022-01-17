// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the case of unpacked array defined using
//  sizes instead of ranges (IEEE 1800-2017 section 7.4.2)
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.01.14  mlupi   Created
//-----------------------------------------------------------------------------

module mymod #(parameter M=2)
  (input  logic clock,
   input  logic [M-1:0] d,
   output logic q);

  logic p [M];
  wire [0:M-1] pVoted = p;
endmodule
