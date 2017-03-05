module functionTest;
 // tmrg do_not_triplicate a b c d myfunction
  
 function  myfunction;
   input a, b, c, d;
   begin
     myfunction = ((a+b) + (c-d));
   end
 endfunction

 reg clk,q;
 reg [3:0] data;

 always @(posedge clk)
  begin
    q=myfunction(data[0],data[1],data[2],data[3]);
  end
endmodule
