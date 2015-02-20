
module BunchCounterConfigurationRegister #(
    parameter int ADDRESS = 'h0CAA
)
(
    input clk,
    input [15:0] data_in,
    input rst_n,
    input we,

    output auto_rst,
    output enable,
    output gray_or_bin,
    output overflow_control,
    output [11:0] preset_val
);

reg auto_rst;
reg enable;
reg gray_or_bin;
reg overflow_control;
reg[11:0] preset_val;

always_ff@(posedge clk or negedge rst_n)
if (rst_n == 1'b0) begin
    gray_or_bin      <= 0;
    enable           <= 0;
    preset_val       <= 0;
    overflow_control <= 0;
    auto_rst         <= 0;
end
else begin
if (we) begin
    gray_or_bin      <= data_in[15:15];
    enable           <= data_in[14:14];
    preset_val       <= data_in[11:0];
    overflow_control <= data_in[13:13];
    auto_rst         <= data_in[12:12];
end
end

endmodule: BunchCounterConfigurationRegister
