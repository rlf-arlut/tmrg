// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the casex construct
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.28  mlupi   Created
//-----------------------------------------------------------------------------

module casex02 (input            clk,
                input      [2:0] state,
                output reg       dataOut);

  always @(posedge clk)
    casex(state)
      3'b00X : dataOut <= 1'b1;
      3'b00? : dataOut <= 1'b1;
      3'b01z : dataOut <= 1'b0;
      3'b1xZ : dataOut <= 1'b0;
      default: dataOut <= 1'b0;
    endcase

endmodule
