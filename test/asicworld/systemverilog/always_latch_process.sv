module always_latch_process();

reg [7:0] sum,a,b;
reg       parity;
reg       enable = 0;

initial begin
  $monitor ("@%g a = %h b = %h sum = %h parity = %b", 
    $time, a, b, sum, parity);
  #2 a = 1;
  #2 b = 1;
  #2 a = 10;
  #2 $finish;
end

always #1 enable = ~enable;

always_latch
begin : ADDER
  if (enable) begin
    sum    <= b + a;
    parity <= ^(b + a);
  end
end

endmodule
