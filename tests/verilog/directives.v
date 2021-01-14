module directive;
  reg a, b;
  always @(a)
    if (a) begin
      // synopsys translate_off
      b = 1'b1;
      // synopsys translate_on
    end

  // synopsys translate_off
  initial
    b = 1'b1;
  // synopsys translate_on
endmodule
