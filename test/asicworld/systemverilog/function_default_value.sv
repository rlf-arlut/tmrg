module function_default_value ();

reg [7:0] data      ;
reg       parity_out;
time      ltime;

function reg parity (reg [7:0] a, time b = 0, time c = 0);
 parity = 0;
 for (int i= 0; i < 8; i ++) begin
    parity = parity ^ a[i];
 end
endfunction

initial begin    
  parity_out = 0;
  data = 0;
  for (int i=250; i<256; i ++) begin
   #5 data = i;
   ltime = $time;
   parity_out = parity (data);
   parity_out = parity (data,,);
   parity_out = parity (data,,10);
   parity_out = parity (data,ltime,);
   $display ("Data = %00000000b, Parity = %b", i, parity_out);
  end
  #10 $finish;
end

endmodule
