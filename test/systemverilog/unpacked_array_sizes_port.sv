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
   input  logic d1 [M],
   output logic q1 [M],
   input  wire d2 [M],
   output reg q3 [M],
   input  d3 [M],
   output q3 [M]
   );

  wire [0:M-1] d1packedVoted = d1;
  wire [0:M-1] d2packedVoted = d2;
  wire [0:M-1] d3packedVoted = d3;
  wire d1unpackedVoted [M] = d1;
  wire d2unpackedVoted [M] = d2;
  wire d3unpackedVoted [M] = d3;
endmodule
