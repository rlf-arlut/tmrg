module ModuleBase(input clk40);
endmodule


module ModuleSpecial(input clk40);
endmodule

module test(
    input          clk40
);
  genvar i;
  generate
    for (i=0; i<=8; i=i+1) begin : loop
      if (i<=8) begin
        ModuleBase Module_0
          (
          .clk40(clk40)
          );
      end
      if (i==8) begin
        ModuleSpecial ModuleSpecial_0
          (
          .clk40(clk40)
          );
        end
    end
  endgenerate

  generate
    for (i=0; i<=8; i=i+1) begin : loop_named
      if (i<=8) begin : if_named
        ModuleBase Module_0
          (
          .clk40(clk40)
          );
      end
      if (i==8) begin : if_named2
        ModuleSpecial ModuleSpecial_0
          (
          .clk40(clk40)
          );
        end
    end
  endgenerate


  generate
    for (i=0; i<=8; i=i+1) begin : loop_if_else
      if (i<=8)
        ModuleBase Module_0
          (
          .clk40(clk40)
          );
      else
        ModuleSpecial ModuleSpecial_0
          (
          .clk40(clk40)
          );
    end
  endgenerate

endmodule
