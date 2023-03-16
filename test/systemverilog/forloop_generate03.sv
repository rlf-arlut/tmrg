module ecc_reg
  #(parameter NUM_REG_BITS         = 8,
    parameter NUM_SYNDROME_BITS    = 5
    )(
      input                           Clk,
      input                           reset_b,
      input [NUM_REG_BITS-1:0]        w_din,
      input                           w_en,
      output logic [NUM_REG_BITS-1:0] reg_dout,
      output logic                    single_bit_err,
      output logic                    double_bit_err,
      output logic                    parity_bit_err
      );
endmodule


module test
  (input logic clk,
   input logic reset_b);

  logic [9:0] a;
  logic b [10];

  always_comb
    for (int i=0; i<10; i++)
      b[i] = a[i];

  logic [99:0] rw_ecc_w_en;
  logic [7:0]  rw_ecc_w_din [100];
  logic [7:0]  rw_ecc_reg_dout [100];
  logic [99:0] rw_ecc_single_bit_err;
  logic [99:0] rw_ecc_double_bit_err;
  logic [99:0] rw_ecc_parity_bit_err;

  generate
    for (genvar i=0; i<100; i++) begin
      ecc_reg # (.NUM_REG_BITS          (8),
		 .NUM_SYNDROME_BITS     (5)
		 ) ecc_reg_u (
			      .Clk                   (clk),
			      .reset_b               (reset_b),
			      .w_din                 (rw_ecc_w_din            [i]),
			      .w_en                  (rw_ecc_w_en             [i]),
			      .reg_dout              (rw_ecc_reg_dout         [i]),
			      .single_bit_err        (rw_ecc_single_bit_err   [i]),
			      .double_bit_err        (rw_ecc_double_bit_err   [i]),
			      .parity_bit_err        (rw_ecc_parity_bit_err   [i])
			      );
      end
  endgenerate
endmodule
