module buf2(input i,output o); 
  assign o=!i; 
endmodule

module forModuleTest;
genvar i,j;
wire [15:0] x;
wire [15:0] o;
generate
  for (int i = 0; i < 16; i = i +1) begin 
    assign x[i]=1;
  end
endgenerate

generate
  for (j = 0; j < 16; j = j +1) begin : loop
   buf2 b(.i(x[j]), .o(o[j]));
  end
endgenerate

endmodule
