// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the import and always_comb construct
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.29  mlupi   Created
//-----------------------------------------------------------------------------

module always_comb_import_function
  (
   output  logic   [11:0]  next_lsb_cnt_o,
   output  logic   [2:0]   next_msb_cnt_o,
   output  logic           lsb_cnt_err_o,
   input   logic   [11:0]  lsb_cnt_i,
   input   logic   [2:0]   msb_cnt_i
   );

  import my_package_pkg::ZERO;
  import my_package_pkg::ONE;
  import my_package_pkg::LSB_CNT_MAX;

  // Unused function
  function logic [11:0] diff_cnt
    (logic   [11:0]  lsb_cnt,
     logic   [2:0]   msb_cnt,
     logic   [11:0]  other_lsb_cnt,
     logic   [2:0]   other_msb_cnt
     );
    diff_cnt = (msb_cnt == other_msb_cnt) ? lsb_cnt-other_lsb_cnt:( lsb_cnt +LSB_CNT_MAX) - other_lsb_cnt;
  endfunction


  always_comb begin
	if(lsb_cnt_i == LSB_CNT_MAX)
	begin
	  next_lsb_cnt_o          =   12'b0000_0000_0000;
	  next_msb_cnt_o           =   msb_cnt_i + 3'b001;
	  lsb_cnt_err_o =   ZERO;
	end
	else if(lsb_cnt_i > LSB_CNT_MAX)
	begin
	  next_lsb_cnt_o          =   lsb_cnt_i;
	  next_msb_cnt_o           =   msb_cnt_i;
	  lsb_cnt_err_o =   ONE;
	end
	else
	begin
	  next_lsb_cnt_o          =   lsb_cnt_i + 12'b0000_0000_0001;
	  next_msb_cnt_o           =   msb_cnt_i;
	  lsb_cnt_err_o =   ZERO;
	end
  end

endmodule   :   always_comb_import_function
