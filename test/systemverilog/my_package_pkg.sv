// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the import construct.
// The imported values are used in always_comb_import, package_import,  and
//  package_import_width
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.29  mlupi   Created
//-----------------------------------------------------------------------------

package my_package_pkg;
  parameter ZERO        = 1'b0;
  parameter TRUE        = 1'b1;
  parameter LSB_CNT_MAX = 3564;
  // Used in package_import_width
  parameter WIDTHD      = 10;
  parameter WIDTHE      = 2;
  parameter WIDTHFP     = 4;
  parameter WIDTHFU     = 1024;
  parameter WIDTHQ      = 4;
  parameter WIDTHR      = 3;
  parameter WIDTHSP     = 10;
  parameter WIDTHSU     = 512;
endpackage
