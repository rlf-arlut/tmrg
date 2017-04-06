module case02 (
  clk,
  state,
  dataOut
);
input  clk;
input [2:0] state;
output reg  dataOut;
localparam IDLE  = 3'b001,
           S0 = 3'b010,
           S1 = 3'b100,
           S2 = 3'b110,
           S3 = 3'b110,
           S4 = 3'b110,
           S5 = 3'b101;


always @ (posedge clk)
  begin : FSM
     case(state)
// synopsys parallel_case
       IDLE :  dataOut=1;
       S0,S1 , S4 ,S5 : begin
                 dataOut=0;
               end
       S2,S3 : dataOut=1;
       default : dataOut=0;
     endcase
 end

 // synopsys translate_off
  reg x;
 // synopsys translate_on

endmodule
