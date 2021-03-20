

module generate_problem #(parameter CHANNELS=10)
(input [CHANNELS-1:0] ii, output [CHANNELS-1:0] oo);
// tmrg do_not_triplicate ii oo
genvar i;

generate 
  for(i=0;i<CHANNELS;i=i+1)
  begin
    reg sig;
    always @(ii[i])
      sig=~ii[i];
    assign oo[i]=sig;
  end
endgenerate

endmodule

module generate_workaround #(parameter CHANNELS=10)
(input [CHANNELS-1:0] ii, output [CHANNELS-1:0] oo);
// tmrg do_not_triplicate ii oo
genvar i;
reg sig[CHANNELS-1:0];

generate 
  for(i=0;i<CHANNELS;i=i+1)
  begin
    always @(ii[i])
      sig[i]=~ii[i];
    assign oo[i]=sig[i];
  end
endgenerate

endmodule

module gen #(parameter CHANNELS=10) (input [CHANNELS-1:0] ii, output [CHANNELS-1:0] oo1, output [CHANNELS-1:0] oo2);
//tmrg do_not_triplicate ii oo1 oo2
generate_problem    gp(.ii(ii),.oo(oo1));
generate_workaround gw(.ii(ii),.oo(oo2));
endmodule
