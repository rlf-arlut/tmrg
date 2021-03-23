module packed_unpacked_data();

// packed array
bit [7:0] packed_array = 8'hAA; 
// unpacked array
reg unpacked_array [7:0] = '{0,0,0,0,0,0,0,1}; 

initial begin
  $display ("packed array[0]   = %b", packed_array[0]);
  $display ("unpacked array[0] = %b", unpacked_array[0]);
  $display ("packed array      = %b", packed_array);
  // Below one is wrong syntax
  //$display("unpacked array[0] = %b",unpacked_array);
  #1 $finish;
end

endmodule
