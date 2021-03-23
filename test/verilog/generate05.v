
module InDataMux (
        input                    clk320,
        input                    rst,
        input    [8:0]   s_in,
        output  [8:0]   s_out,
        input   [7:0]   InSetting0,
        input   [7:0]   InSetting1,
        input   [7:0]   InSetting2,
        input   [7:0]   InSetting3,
        input   [7:0]   InSetting4,
        input   [7:0]   InSetting5,
        input   [7:0]   InSetting6,
        input   [7:0]   InSetting7,
        input   [7:0]   InSetting8,
        input    [8:0]   EdgeSel
        );

// tmrg default do_not_triplicate

wire    [7:0]   InSetting [8:0];
reg     [8:0]   in;
reg     [8:0]   in_r;
reg     [8:0]   in_f;
reg     [8:0]   in_fr;
reg      [8:0]   s_in_d;

assign InSetting[0] = InSetting0;
assign InSetting[1] = InSetting1;      
assign InSetting[2] = InSetting2;      
assign InSetting[3] = InSetting3;      
assign InSetting[4] = InSetting4;      
assign InSetting[5] = InSetting5;      
assign InSetting[6] = InSetting6;      
assign InSetting[7] = InSetting7;      
assign InSetting[8] = InSetting8;
genvar i;
generate
        for (i=0; i<9; i=i+1) begin

                assign s_out[i] =       
                ((InSetting[i] == 7'd0)?in[0]:
                ((InSetting[i] == 7'd1)?in[1]: 
                ((InSetting[i] == 7'd2)?in[2]:
                ((InSetting[i] == 7'd3)?in[3]:
                ((InSetting[i] == 7'd4)?in[4]:
                ((InSetting[i] == 7'd5)?in[5]:
                ((InSetting[i] == 7'd6)?in[6]:
                ((InSetting[i] == 7'd7)?in[7]:
                ((InSetting[i] == 7'd8)?in[8]:1'b0)))))))));
        end
endgenerate

endmodule
