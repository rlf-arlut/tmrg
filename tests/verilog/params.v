module paramtest1 #(parameter f=3) (input clk,input d, output q);
  paramtest3 #(.f(3),.p1(3),.p2(3),.k(3)) x (.clk(clk),.d(d),.q(q));
endmodule


module paramtest2 #(parameter f=3, parameter k=3) (input clk,input [f:k]d , output q);
  parameter p1=1;
  parameter p2=1;
endmodule

module paramtest3 #(parameter f=3, parameter k= (f>2) ? 3 : 1) (input clk,input [f:k]d , output q);
  parameter p1=1;
  parameter p2=1;
endmodule

module paramtestTop (input clk,input d, output q);
  parameter signed p1=1;
  parameter p2=1;
  paramtest1 #(.f(3)) x1 (.clk(clk),.d(d),.q(q));
  paramtest2 #(.f(3)) x2 (.clk(clk),.d(d),.q(q));
  paramtest3 #(.f(3)) x3 (.clk(clk),.d(d),.q(q));
endmodule

