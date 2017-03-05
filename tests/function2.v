module functionTest;
 // tmrg do_not_triplicate a b c d myfunction
 function  myfunction;
   input a, b, c, d;
   begin
     myfunction = ((a+b) + (c-d));
   end
 endfunction

 reg clk,q;
 reg [3:0] d;

 always @(posedge clk)
  begin
    q=myfunction(d[0],d[1],d[2],d[3]);
  end
endmodule
