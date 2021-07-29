module for_loops (
  input x,
  input clk,
  input rst
);
  localparam N = 5;
  logic   [N-1:0]  data;

  always_comb begin
    for (int i=0; i<N; i++)
      if(i < x)
        data[i] = 0;
      else 
        data[i] = 1;
  end
  
  integer z;
  always_ff @(posedge clk) begin
    if (rst)
      for (int j=0;j<N;j=j+1)
        data[j] <=   0;
    else
      for (z=0; z<N; z++)
        if(z < x)
          data[z] <=   0;
        else
          data[z] <=   1;
  end
endmodule   :   for_loops
