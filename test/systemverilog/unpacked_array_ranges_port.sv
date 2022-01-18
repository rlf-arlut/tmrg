// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the case of unpacked array defined using
//  ranges in defition (IEEE 1800-2017 section 7.4.2) and used in the ports of
//  of a module (IEEE 1800-2017 section 23.2.2).
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.01.14  mlupi   Created
//-----------------------------------------------------------------------------

module mymod #(parameter M=2)
  (input  logic clock,
   input logic [M-1:0] d1,
   input logic d2 [0:M-1],
   input [M-1:0] d3,
   input d4 [0:M-1],
   input wire [M-1:0] d3,
   input wire d4 [0:M-1],
   output logic [M-1:0] q1,
   output logic q2 [0:M-1],
   output reg [M-1:0] q3,
   output reg q4 [0:M-1],
   output [M-1:0] q5,
   output q6 [0:M-1]
   );
wire [M-1:0] d3Voted = d3;
  wire [M-1:0] d4packedVoted = d4;
  wire d4unpackedVoted [0:M-1] = d4;
endmodule
