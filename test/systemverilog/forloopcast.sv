// author : Krzysztof Swientek (AGH,UST)
// edit:    Matteo Lupi
module tfc_fifo #(
    parameter FIFO_DEPTH=256,
    parameter TFC_WIDTH=8
)(
    input logic main_clk,
    input logic rst_n,

    input logic [7:0] fifo_len,
    input logic [TFC_WIDTH-1:0] tfc_in,
    output logic [TFC_WIDTH-1:0] tfc_out
);
    // tmrg default do_not_triplicate
    // tmrg triplicate rst_n main_clk
    // tmrg triplicate tfc_out_tmr fifo_tmr
    // tmrg triplicate j i
    logic [TFC_WIDTH-1:0] tfc_out_tmr;
    assign tfc_out=tfc_out_tmr;


    logic [TFC_WIDTH-1:0] fifo_tmr [FIFO_DEPTH-1:0];
    logic [TFC_WIDTH-1:0] fifo [FIFO_DEPTH-1:0];
    generate
      for (genvar j=0;j<int'(FIFO_DEPTH);j=j+1)
          begin : fifomap
              assign fifo[j]=fifo_tmr[j];
          end
    endgenerate

    always @(posedge main_clk or negedge rst_n)
        if (!rst_n)
            fifo_tmr[0] <= 0;
        else
            fifo_tmr[0] <= tfc_in;

    always @(posedge main_clk or negedge rst_n) begin : fifo_main
        if (!rst_n)
            for(int i=1; i<int'(FIFO_DEPTH); i++)
                fifo_tmr[i] <= 0;
        else
            for(int i=1; i<int'(FIFO_DEPTH-1); i=i+1)
                fifo_tmr[i] <= fifo[i-1];
    end

    always @(posedge main_clk or negedge rst_n)
        if (!rst_n)
            tfc_out_tmr <= 0;
        else
            tfc_out_tmr <= fifo[fifo_len];
endmodule
