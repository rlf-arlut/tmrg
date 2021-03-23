module paramtest #(parameter f=3) (input clk,input d, output q);
  paramtest3 #(.f(3),.p1(3),.p2(3),.k(3)) x (.clk(clk),.d(d),.q(q));
endmodule

module paramtest2 (input clk,input d, output q);
  parameter p1=1;
  parameter p2=1;
  paramtest #(.f(3)) x (.clk(clk),.d(d),.q(q));
endmodule

module paramtest3 #(parameter f=3, parameter k=3) (input clk,input [f:k]d , output q);
  parameter p1=1;
  parameter p2=1;
  parameter p3=p1+p2;
endmodule

