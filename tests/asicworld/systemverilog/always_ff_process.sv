module always_ff_process();

reg [7:0] sum,a,b;
reg       parity;
logic     clk = 0;
reg       rst = 0;

initial begin
  $monitor ("@%g clk = %b rst = %b a = %h b = %h sum = %h parity = %b", 
  $time, clk, rst, a, b, sum, parity);
  #1 rst = 1;
  #5 rst = 0;
  #2 a = 1;
  #2 b = 1;
  #2 a = 10;
  #2 $finish;
end

always #1 clk ++;

// use of iff makes sure that block does not get
// triggered due to posedge of clk when rst == 1
always_ff @(posedge clk iff rst == 0 or posedge rst)
begin : ADDER
  if (rst) begin
    sum    <= 0;
    parity <= 0;
    $display ("Reset is asserted BLOCK 1");
  end else begin
    sum    <= b + a;
    parity <= ^(b + a);
  end
end

// To show how iff affected in earlier code
always_ff @(posedge clk  or posedge rst)
begin
  if (rst) begin
    $display ("Reset is asserted BLOCK 2");
  end 
end

endmodule
