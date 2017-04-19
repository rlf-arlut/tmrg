module syscall (
  input signed [7:0] A,
  output [7:0] B
);
  assign B = (A < 0) ? $unsigned(~A+1'd1) : $unsigned(A) ;

endmodule
