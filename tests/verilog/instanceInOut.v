module pll(input clkin,
           input [7:0] cfg,
           output clkout);
  // tmrg do_not_touch
  assign clkout = clkin & cfg[0];
endmodule

module cfgReg (input rst, output reg  [7:0] cfg);
  // tmrg do_not_triplicate cfg
  // tmrg do_not_triplicate rst
  always @(posedge rst)
    cfg <= 0;
endmodule

module top (input clkin,output clkout, input rst);
  // tmrg default do_not_triplicate
  // tmrg triplicate pllinst
  // tmrg triplicate clkin

  wire [7:0] cfg;
  cfgReg cr(.rst(rst),.cfg(cfg));
  pll pllinst(.clkin(clkin), .clkout(clkout), .cfg(cfg));
endmodule
