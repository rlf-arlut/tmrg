// author : Krzysztof Swientek (AGH,UST)
module tfc_fifo #(
    parameter FIFO_DEPTH=256,
    parameter TFC_WIDTH=8
)(
    input wire main_clk,
    input wire rst_n,

    input wire [7:0] fifo_len,
    input wire [TFC_WIDTH-1:0] tfc_in,
    output wire [TFC_WIDTH-1:0] tfc_out
);
    // tmrg default do_not_triplicate
    // tmrg triplicate rst_n main_clk
    // tmrg triplicate tfc_out_tmr fifo_tmr
		// tmrg triplicate j i
    reg [TFC_WIDTH-1:0] tfc_out_tmr;
    assign tfc_out=tfc_out_tmr;


    reg [TFC_WIDTH-1:0] fifo_tmr [FIFO_DEPTH-1:0];
    wire [TFC_WIDTH-1:0] fifo [FIFO_DEPTH-1:0];
    genvar j;
    generate
      for (j=0;j<FIFO_DEPTH;j=j+1)
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
        integer i;
        if (!rst_n)
            for(i=1; i<FIFO_DEPTH; i=i+1)
                fifo_tmr[i] <= 0;
        else
            for(i=1; i<FIFO_DEPTH-1; i=i+1)
                fifo_tmr[i] <= fifo[i-1];
    end

    always @(posedge main_clk or negedge rst_n)
        if (!rst_n)
            tfc_out_tmr <= 0;
        else
            tfc_out_tmr <= fifo[fifo_len];
endmodule
