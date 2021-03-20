//+++++++++++++++++++++++++++++++++++++++++++++++++
//   Package Declaration
//+++++++++++++++++++++++++++++++++++++++++++++++++
package definesPkg;
  //=================================================
  // TypeDefs declaration
  //=================================================
  typedef enum  {FALSE, TRUE} bool;
  typedef struct {
     bit   [7:0]   addr;
     bit   [7:0]   data;
     bit           wr;
  } mem_s; 

endpackage
