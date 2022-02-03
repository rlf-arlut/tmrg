// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the typed localparam.
// See IEEE 1800-2017 section 6.20 and 6.20.1
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.01.21  mlupi   Created
// 2022.02.02  mlupi   Added testcase for #49
//-----------------------------------------------------------------------------

module test;
  // integer_atom_type
  localparam byte         a = 1;
  localparam shortint     b = 0;
  localparam unsigned     c = 10;
  localparam signed       d = 10;
  localparam longint      e = 21;
  localparam integer      f = 31;

  // integer_vector_type
  localparam bit   [1:0] g = 2'b10;
  localparam logic [3:0] h = 'h2;
  localparam reg   [6:0] i = 6'h02;

  // unpacked array of packed arrays
  localparam bit [15:0] j [2] = '{16'hffff,
                                  16'd65000,
                                  16'b1100_0000_1111_0011,
                                  b};
  localparam bit [15:0] k [0:1] = '{16'haabb,
                                    16'd12,
                                    16'b1100_0000_1111_0011,
                                    b};
endmodule
