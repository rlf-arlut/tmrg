module mini(input i, output o);
  // tmrg default triplicate
  // tmrg tmr_error true
  wire iVoted=i;
  assign o=iVoted;
endmodule

module top;
parameter N=10;
wire [N-1:0] i;
wire [N-1:0] o;
genvar j;
generate
  for(j=0;j<N;j=j+1)
    begin:loop
      mini inst(.i(i[j]),
                .o(o[j]));
    end
endgenerate
endmodule


module top2;
parameter N=10;
wire [N-1:0] i;
wire [N-1:0] o;
genvar j;
wire instTmrError=1'b0;
generate
  for(j=0;j<N;j=j+1)
    begin:loop
      mini inst(.i(i[j]),
                .o(o[j]));
    end
endgenerate
endmodule

module top3;
parameter N=10;
wire [N-1:0] i;
wire [N-1:0] o;
genvar j;
wor instTmrError=1'b0;
generate
  for(j=0;j<N;j=j+1)
    begin:loop
      mini inst(.i(i[j]),
                .o(o[j]));
    end
endgenerate
endmodule
