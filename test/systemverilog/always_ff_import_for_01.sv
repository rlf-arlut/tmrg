// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the for loop with variable declaration inside
// the for loop.
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.29  mlupi   Created
//-----------------------------------------------------------------------------

module always_ff_import_for_01
  (input logic clk,
   input logic rst);

  import my_package_pkg::ZERO;
  import my_package_pkg::ONE;
  import my_package_pkg::ARRAY_DIM;
  import my_package_pkg::START;
  import my_package_pkg::STOP;

  logic   [(ARRAY_DIM-1):0]  data;

  always_ff @(posedge clk) begin
    if (rst)
      for (int j=0;j<ARRAY_DIM;j=j+1)
        data[i] <=   ZERO;
    else
      for (int i=0; i<ARRAY_DIM; i++)
        if(i < START)
          data[i] <=   ZERO;
        else if((i >= START) && (i < STOP))
          data[i] <=   ONE;
        else if(i == STOP)
          data[i] <=   ZERO;
        else
          data[i] <=   ONE;
  end

endmodule   :   always_ff_import_for_01
