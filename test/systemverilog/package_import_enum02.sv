// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the enum usage in FSMs
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.08.04  mlupi   Created
//-----------------------------------------------------------------------------

module package_import_emum02
  (input  logic c,
   input  logic rst,
   input  logic in,
   output logic out);

  import my_package_pkg::FSM_States_t;

  FSM_States_t state, next_state;
  FSM_States_t stateVoted = state;

  always_ff @(posedge c)
    if (rst)
      state <= FSM_S0;
    else
      state <= next_state;

  always_comb
    case (stateVoted)
      FSM_ST0 : next_state = in ? FSM_ST1 : FSM_ST7;
      FSM_ST1 : next_state = in ? FSM_ST2 : FSM_ST0;
      FSM_ST2 : next_state = in ? FSM_ST3 : FSM_ST1;
      FSM_ST3 : next_state = in ? FSM_ST4 : FSM_ST2;
      FSM_ST4 : next_state = in ? FSM_ST5 : FSM_ST3;
      FSM_ST5 : next_state = in ? FSM_ST6 : FSM_ST4;
      FSM_ST6 : next_state = in ? FSM_ST7 : FSM_ST5;
      FSM_ST7 : next_state = in ? FSM_ST0 : FSM_ST6;
      default : next_state = in ? FSM_ST1 : FSM_ST0;
    endcase

  always_comb
    case (stateVoted)
      FSM_ST0 : out = 1'b1;
      FSM_ST1 : out = 1'b0;
      FSM_ST2 : out = 1'b0;
      FSM_ST3 : out = 1'b1;
      FSM_ST4 : out = 1'b1;
      FSM_ST5 : out = 1'b0;
      FSM_ST6 : out = 1'b1;
      FSM_ST7 : out = 1'b0;
      default : out = 1'b1;
    endcase

endmodule : package_import_emum02
