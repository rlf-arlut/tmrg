// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to test the generate construct in Systemverilog
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.08.09  mlupi   Created
//-----------------------------------------------------------------------------

module forloop_generate_01
  (input logic c,
   input logic r,
   output logic [31:0] a);

genvar j;
generate
  for (j=0; j<32; j++)
    always @(posedge c)
      if (r) a[j] <= 1'b0;
      else   a[j] <= j%2;
endgenerate
