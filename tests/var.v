module x;
integer x;
reg [5:0] r;
//tmrg do_not_triplicate x
initial
  begin
    for(x=0;x<5;x=x+1)
      r[x]=1'b0;
  end
endmodule
