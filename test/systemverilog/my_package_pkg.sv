// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the import construct.
// The imported values are used in always_comb_import.sv.
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.29  mlupi   Created
// 2021.08.04  mlupi   Added enum typedef
//-----------------------------------------------------------------------------

package my_package_pkg;
  parameter ZERO        = 1'b0;
  parameter TRUE        = 1'b1;
  parameter LSB_CNT_MAX = 3564;

  enum logic [2:0]
       {FSM_ST0 = 3'b000,
        FSM_ST1 = 3'b001,
        FSM_ST2 = 3'b010,
        FSM_ST3 = 3'b011,
        FSM_ST4 = 3'b100,
        FSM_ST5 = 3'b101,
        FSM_ST6 = 3'b110,
        FSM_ST7 = 3'b111
        } FSM_States_t;
endpackage
