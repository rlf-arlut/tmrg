module function_by_ref ();

reg [7:0] data      ;
reg       parity_out;

time      ltime;

function reg parity (ref reg [7:0] idata, const ref time tdata);
 parity = 0;
 for (int i= 0; i < 8; i ++) begin
    parity = parity ^ idata[i];
 end
 // We can modify the data passed through reference
 idata ++ ;
 // Something that is passed as const  ref, can  not be modified
 // tdata ++ ; This is wrong
endfunction

initial begin    
  parity_out = 0;
  data = 0;
  for (int i=250; i<256; i ++) begin
   #5 data = i;
   ltime = $time;
   parity_out = parity (data, ltime);
   $display ("Data = %00000000b, Parity = %b, Modified data : %b",
      i, parity_out, data);
  end
  #10 $finish;
end

endmodule
