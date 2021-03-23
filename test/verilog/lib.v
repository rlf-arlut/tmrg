module dff(input clk, output reg q, input d);
 // tmrg seu_set s
 // tmrg seu_reset r
 reg s;
 reg r;
 initial
   begin
     s=1'b0;
     r=1'b0;
   end
 always @(posedge clk or posedge r or posedge s)
   if (r)
     q<=1'b0;
   else if (s)
     q<=1'b1;
   else
     q<=d;
endmodule
