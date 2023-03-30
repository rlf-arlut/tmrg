// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the always_comb construct.
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.29  mlupi   Created
// 2023.03.30  skulis  Modified to address #67
//-----------------------------------------------------------------------------

module always_comb_01
  (output logic [3:0]  binary_out,
   input  logic [15:0] encoder_in,
   input  logic        enable);

  // tmrg default triplicate
  logic binary_int;
  wire binary_intVoted = binary_int;
  assign binary_out = binary_intVoted;

  always_comb begin :labelled_always_comb
    binary_int = |encoder_in;
  end : labelled_always_comb

endmodule : always_comb_01
