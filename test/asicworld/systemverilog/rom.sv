module rom (
input  wire [7:0] address , // Address input
output wire [7:0] data    , // Data output
input  wire       read_en , // Read Enable 
input  wire       ce        // Chip Enable
);
  
reg [7:0]    mem [0:255] ;

assign data = (ce && read_en) ? mem[address] : 8'b0;

initial begin
  $readmemb("memory.list",mem);
end

endmodule

// Testbench code
module rom_tb;
 reg [7:0] address;
 reg read_en, ce;
 wire [7:0] data;
 integer i;
 
 initial begin
   address = 0;
   read_en = 0;
   ce      = 0;
   #10 $monitor ("address = %h, data = %h, read_en = %b, ce = %b", address, data, read_en, ce);
   for (i = 0; i <256; i = i +1 )begin
     #5 address = i;
     read_en = 1;
     ce = 1;
     #5 read_en = 0;
     ce = 0;
     address = 0;
   end
 end
 
rom U(
address , // Address input
data    , // Data output
read_en , // Read Enable
ce        // Chip Enable
);

endmodule


