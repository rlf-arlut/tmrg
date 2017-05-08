[...]
localparam k=8;
// tmrg do_not_triplicate dataMux
reg [2:0] sel;
reg [k-1:0] data [2*k-1:0];
wire [k-1:0] dataMux = data[sel];
[...]
