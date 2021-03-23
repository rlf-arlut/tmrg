module top(
  input clkin,
  output clkout1,
  output clkout2
);

  // tmrg default triplicate
  // tmrg do_not_triplicate clkout2

  divider div(
    .clkin(clkin),
    .clkout1(clkout1),
    .clkout2(clkout2)
  );

endmodule
