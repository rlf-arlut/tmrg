`timescale 1ns / 1ns
//---------------------------------------
// Verilog DUT 
//---------------------------------------
module counter(
rst,   // Reset input
clk,   // Clock Input
d_out  // Counter output
);
// Port Declation
input      rst;
input      clk;
output  [31:0]  d_out;
// Internal data type
reg  [31:0]  d_out;
// Code starts here
always @ (posedge clk)
  if (rst) d_out = 0;
  else d_out = d_out + 1;

endmodule
//---------------------------------------
// Testbench top level
//---------------------------------------
module tb();
reg      rst;
reg      clk;
integer  iclk,irst,idout;
wire  [31:0]  d_out;
// Import the C functions
import "DPI" function void sc_counter_init();
import "DPI" function int sc_counter_interface
    (input int iclk, idout);
// Assign Integer to reg
always @ (clk)   iclk  =  clk;
always @ (irst)  rst   =  irst;
always @ (d_out) idout =  d_out;
// Call SystemC interface method, when ever
// Input changes
always @ (idout or iclk)
begin
  irst = sc_counter_interface(iclk,idout);
end
// Init the simulation
initial begin
 sc_counter_init();
 clk = 0;
end
// Clock generator
always #1 clk = ~clk;
// DUT connection
counter dut (
    // Inputs
    rst,
    clk,
    // Outputs
    d_out
);

endmodule
