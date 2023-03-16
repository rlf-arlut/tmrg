module test;
  // integer_atom_type
  parameter byte         a = 1;
  parameter shortint     b = 0;
  parameter unsigned     c = 10;
  parameter signed       d = 10;
  parameter longint      e = 21;
  parameter integer      f = 31;

  // integer_vector_type
  parameter bit   [1:0] g = 2'b10;
  parameter logic [3:0] h = 'h2;
  parameter reg   [6:0] i = 6'h02;

  // unpacked array of packed arrays
  parameter bit [15:0] j [2] = '{16'hffff,
                                 16'd65000,
                                 16'b1100_0000_1111_0011,
                                 b};
  parameter bit [15:0] k [0:1] = '{16'haabb,
                                   16'd12,
                                   16'b1100_0000_1111_0011,
                                   b};
endmodule
