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

module always_comb_import_for;

  import my_package_pkg::ZERO;
  import my_package_pkg::ONE;
  import my_package_pkg::ARRAY_DIM;
  import my_package_pkg::START;
  import my_package_pkg::STOP;

  logic   [(ARRAY_DIM-1):0]  data;

  always_comb begin
    for (int i=0; i<ARRAY_DIM; i++)
      if(i < START)
        data[i] =   ZERO;
      else if((i >= START) && (i < STOP))
        data[i] =   ONE;
      else if(i == STOP)
        data[i] =   ZERO;
      else
        data[i] =   ONE;
  end

endmodule   :   always_comb_import_for
