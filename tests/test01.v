// comment
module test01( in, out, in1, out1, in2, out2 , input iz1, input [1:0] iz2);
  input        in,in2;
  output [5:0] out; //comment
  inout        io3;/* huh
  */
  input [7:0]  inc;
  input        in2;
  output [1:0] out1; //comment
  inout        io1;
  input [12:0] ina;
  input [7:2]  in1;
  output       out2; //comment
  inout        io2;
  input [7:0]  inb;
  reg r1,r2,r3;
  reg [2:0] r4,r5;
  parameter N=8;
  parameter N1=5;
  parameter N2=3;
  wire K=2&d;
  integer ddd;

  assign a=r1 & r2, //bit-wise AND operator
    b=&s, //unary reduction AND operator
    c=r1 && r2, //logical AND operator
    d=~&u, //unary reduction NAND operator
    e=r2 | r3, //bit-wise OR operator
    f=r3 || r4, //logical OR operator
    g=|u, //unary reduction OR operator
    h=~|u, //unary reduction NOR operator
    i=r4 ^ r5, //bit-wise XOR operator
    j=^u,//unary reduction XNOR operator
    l=~^v,//unary reduction XNOR operator
    m=~j,//bit-wise NOT operator
    n = !r1,//logical NOT operator
    w={a,b},//concatenation operator
    y={2{r7}},//duplicate concatenation operator
    q=r1 ? a : b,//conditional operator
    s= r1 == r2,//logical equality operator
    t= r3 != r4;//logical inequality operator
//k=r5 ~^r6,

  assign a = 1 + p1;         //expression with addition operator and constant operands
  assign b = r1 | (p2 << 1); //sub-expression with shift operator and constant operands
  assign c = {r1,(p2 % p1)}; //sub-expression with modulo operator and constant operands

  parameter p=10;
  assign #p q = ~(a & qb); //delay is a constant
  assign #(p+1) qb = ~(b & q); //delay expression with constant operands

assign m1=~(({a,b}&{d,e})|({c,d}^{e,f}));
assign m={e,f};
assign m3=~{i,j};
assign m4=~({m,n}|{a,b});
assign m5=((q & r)^(p | t)|{q,r});

reg r1,r2;
assign #r1 a=c; //delay is not a constant
assign #(a & r2) b=d; //operands in delay expression are variables




  always @(posedge clk)
    begin
      x<=#NK 2;
          if (in)
      x<=2'b0;
    if (x && y==1'b1)
      a=0;
    else
      begin
        v=2;
        if (d) begin y=2; end
      end
    end

  initial begin
    clk = 0;
    read_data = 0;
    rd = 0;
    wr = 0;
    ce = 0;
    addr = 0;
    data_wr = 0;
    data_rd = 0;
    // Call the write and read tasks here
     #1  cpu_write(8'h11,8'hAA);
     #1  cpu_read(8'h11,read_data);
     #1  cpu_write(8'h12,8'hAB);
     #1  cpu_read(8'h12,read_data);
     #1  cpu_write(8'h13,8'h0A);
     #1  cpu_read(8'h13,read_data);
     #100  $finish;
  end

  task cpu_read;
    input [7:0]  address;
    output [7:0] data;
    begin
      $display ("%g CPU Read  task with address : %h", $time, address);
      $display ("%g  -> Driving CE, RD and ADDRESS on to bus", $time);
      @ (posedge clk);
      addr = address;
      ce = 1;
      rd = 1;
      @ (negedge clk);
      data = data_rd;
      @ (posedge clk);
      addr = 0;
      ce = 0;
      rd = 0;
      $display ("%g CPU Read  data              : %h", $time, data);
      $display ("======================");
    end

  endtask

  assign mux_out = (sel) ? din_1 : din_0;

  wire sel,a_sel,b_sel;
  
  not U_inv (inv_sel,sel);
  and U_anda (asel,a,inv_sel),
      U_andb (bsel,b,sel);
  or U_or (y,asel,bsel);

  always @ (enable or binary_in)
  begin
    decoder_out = 0;
    if (enable) begin
      case (binary_in)
        4'h0 : decoder_out = 16'h0001;
        4'h1 : decoder_out = 16'h0002;
        4'h2 : decoder_out = 16'h0004;
        4'h3 : decoder_out = 16'h0008;
        4'h4 : decoder_out = 16'h0010;
        4'h5 : decoder_out = 16'h0020;
        4'h6 : decoder_out = 16'h0040;
        4'h7 : decoder_out = 16'h0080;
        4'h8 : decoder_out = 16'h0100;
        4'h9 : decoder_out = 16'h0200;
        4'hA : decoder_out = 16'h0400;
        4'hB : decoder_out = 16'h0800;
        4'hC : decoder_out = 16'h1000;
        4'hD : decoder_out = 16'h2000;
        4'hE : decoder_out = 16'h4000;
        4'hF : decoder_out = 16'h8000;
      endcase
    end
  end

  always @ ( posedge clk)
  if (~reset) begin
    q <= 1'b0;
  end  else begin
    q <= data;
  end

  initial begin
    f = $fopen("output.txt","w");

    @(negedge reset); //Wait for reset to be released
    @(posedge clk);   //Wait for fisrt clock out of reset

    for (i = 0; i<14; i=i+1) begin
      $fwrite(f,"%b\n",lfsr[i]);
    end

    $fclose(f);  
  end
  always
    {carry_out, sum_out} = #10 ina + inb + carry_in;


endmodule
