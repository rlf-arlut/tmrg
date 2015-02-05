module fsm01 (
  clk     , // clock
  rst     , // Active high, syn reset
  req0    , // Request 0
  req1    , // Request 1
  gnt0    , // Grant 0
  gnt_1
);

//=============Input Ports=============================
input   clk,rst,req0,req1;
//=============Output Ports===========================
output  gnt0,gnt1;

//=============Input ports Data Type===================
wire    clk,rst,req0,req1;
//=============Output Ports Data Type==================
reg     gnt0,gnt1;

//=============Internal Constants======================
parameter SIZE = 3           ;
parameter IDLE  = 3'b001,GNT0 = 3'b010,GNT1 = 3'b100 ;

//=============Internal Variables======================
reg   [SIZE-1:0] state;

//==========Code startes Here==========================
always @ (posedge clock)
  begin : FSM
    if (reset == 1'b1) begin
      state <=  #1  IDLE;
      gnt0 <= 0;
      gnt1 <= 0;
    end else
     case(state)
       IDLE : if (req_0 == 1'b1) 
                begin
                  state <=  #1  GNT0;
                  gnt_0 <= 1;
                end 
              else if (req_1 == 1'b1) 
                begin
                  gnt_1 <= 1;
                  state <=  #1  GNT1;
              end else 
                begin
                  state <=  #1  IDLE;
                end
       GNT0 : if (req_0 == 1'b1) 
                 begin
                  state <=  #1  GNT0;
                end 
              else 
                begin
                  gnt_0 <= 0;
                  state <=  #1  IDLE;
                end
       GNT1 : if (req_1 == 1'b1) 
                begin
                  state <=  #1  GNT1;
                end 
              else 
                begin
                  gnt_1 <= 0;
                  state <=  #1  IDLE;
                end
    default : state <=  #1  IDLE;
 endcase
 end
endmodule // End of Module arbiter
