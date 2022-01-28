// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the package import in the width of an array
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2022.01.24  mlupi   Created
//-----------------------------------------------------------------------------

module package_import_width
     (input logic  [my_package_pkg::WIDTHD-1:0] d,
      input logic  [8*my_package_pkg::WIDTHD-1:0] d1,
      input logic  [0:my_package_pkg::WIDTHD-1] d2,
      input logic  e [my_package_pkg::WIDTHE-1:0],
      input logic  e1 [my_package_pkg::WIDTHE],
      input logic  [my_package_pkg::WIDTHFP-1:0] f [my_package_pkg::WIDTHFU-1:0],
      output logic [my_package_pkg::WIDTHQ-1:0] q,
      output logic r [my_package_pkg::WIDTHR-1:0],
      output logic [my_package_pkg::WIDTHSP-1:0] s [my_package_pkg::WIDTHSU-1:0]
      );
endmodule
