// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the casez construct
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.28  mlupi   Created
//-----------------------------------------------------------------------------

module casez02 (input            clk,
                input      [2:0] state,
                output reg       dataOut);

  always @(posedge clk)
    casez(state)
      3'b000 : dataOut <= 1'b1;
      3'b001 : dataOut <= 1'b1;
      3'b01z : dataOut <= 1'b0;
      3'b1?Z : dataOut <= 1'b0;
      default: dataOut <= 1'b0;
    endcase

endmodule
