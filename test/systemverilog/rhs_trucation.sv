// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the truncation/static cast of a vector/expression
//  as specified by IEEE 1800-2017 section 6.24.1
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.01.21  mlupi   Created
//-----------------------------------------------------------------------------

module rhs_trucate #(parameter W=3)
  (input logic clk,
   input  logic [5:0] d0,
   input  logic [W-1:0] d1,
   output logic [W-1:0] qa0,
   output logic [W-1:0] qa1,
   output logic [W:0] qa2,
   output logic [3:0] qa3,
   output logic [W-1:0] qac0,
   output logic [W-1:0] qac1,
   output logic [W:0] qac2,
   output logic [3:0] qac3,
   output logic [W-1:0] qaf0,
   output logic [W-1:0] qaf1,
   output logic [W:0] qaf2,
   output logic [3:0] qaf3
   );

  integer pa;
  integer pac;
  integer paf;

  assign qa0 = W'(d0+1);
  assign qa1 = W'(d1+1);
  assign qa2 = (W+1)'(d0+1);
  assign qa3 = 4'(d0+1);
  assign pa = int'(d0);

  always_comb begin
    qac0 = W'(d0+1);
    qac1 = W'(d1+1);
    qac2 = (W+1)'(d0+1);
    qac3 = 4'(d0+1);
    pac = int'(d0);
  end

  always_ff @(posedge clk) begin
    qaf0 <= W'(d0+1);
    qaf1 <= W'(d1+1);
    qaf2 <= (W+1)'(d0+1);
    qaf3 <= 4'(d0+1);
    paf = int'(d0);
  end

endmodule
