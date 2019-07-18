module mini(input i, output o);
  // tmrg default triplicate
  // tmrg tmr_error true
  wire iVoted=i;
  assign o=iVoted;
endmodule

module top;
// tmrg tmr_error true
parameter N=10;
wire [N:0] i;
wire [N:0] o;
genvar j;
generate
  for(j=0;j<N;j=j+1)
    begin:loop
      mini inst(.i(i[j]),
                .o(o[j]));
    end
endgenerate

mini single(.i(i[N]),
            .o(o[N]));
endmodule

