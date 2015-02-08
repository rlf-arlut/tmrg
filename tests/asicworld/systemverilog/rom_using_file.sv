//===========================================
// Function : ROM using readmemh
// Coder    : Deepak Kumar Tala
// Date     : 31-Oct-2005
//===========================================
module rom_using_file (
input  wire [7:0] address , // Address input
output wire [7:0] data    , // Data output
input  wire       read_en , // Read Enable 
input  wire       ce        // Chip Enable
);
           
reg [7:0] mem [0:255] ;  
      
assign data = (ce && read_en) ? mem[address] : 8'b0;

initial begin
  $readmemb("memory.list", mem); // memory_list is memory file
end

endmodule
