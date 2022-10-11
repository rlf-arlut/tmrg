// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the blocking procedural assing in issue #59
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.10.11  mlupi   Created
//-----------------------------------------------------------------------------

module issue_59
  (output logic [767:0]   Reg_Data_In,
   input  logic [36863:0] Demux_Out);

  // tmrg default triplicate

  always_comb begin
    Reg_Data_In = '0;
    for (int k = 0; k <= 47; k++) begin
      Reg_Data_In |= Demux_Out[k*768+:768];
    end
  end
endmodule
