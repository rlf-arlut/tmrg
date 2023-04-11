module unpacked_arrays_assignments
  (input logic clk,
   input logic i,
   input logic [2:0] sel
  );

  localparam N=8;

  logic comb [N];

  always_comb begin
    comb = '{(N){1'b0}};
  end
endmodule
