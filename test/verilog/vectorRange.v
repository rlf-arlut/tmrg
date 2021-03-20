module vectorRange
  #(parameter ifrom=0,ito=7, jfrom=7,jto=7)
  (input i, output o);

  //////////////////////////////////////////////////////////////////////////////
  // non triplicated vector = triplicated vector
  //////////////////////////////////////////////////////////////////////////////

  reg [ifrom:ito] i1t;
  reg [jfrom:jto] i2t; 
  reg [7:0]       i3t; 
  reg [0:7]       i4t; 

  // tmrg do_not_triplicate i1 i2 i3 i4
  wire [ifrom:ito] i1;
  wire [jfrom:jto] i2;
  wire [7:0]       i3;
  wire [0:7]       i4;

  assign i1=i1t;
  assign i2=i2t;
  assign i3=i3t;
  assign i4=i4t;

  //////////////////////////////////////////////////////////////////////////////
  // triplicated array = non triplicated array
  //////////////////////////////////////////////////////////////////////////////

  reg m1t;
  reg m2t; 
  reg m3t; 
  reg m4t; 

  // tmrg do_not_triplicate m1 m2 m3 m4
  wire [ifrom:ito] m1;
  wire [jfrom:jto] m2; 
  wire [7:0] m3; 
  wire [0:7] m4; 
  always @*
    begin
      m1t=m1[ito];
      m2t=m2[jfrom];
      m3t=m3[4];
      m4t=m4[4];
    end

  //////////////////////////////////////////////////////////////////////////////
  // non triplicated array = triplicated array
  //////////////////////////////////////////////////////////////////////////////

  reg a1t [ifrom:ito];
  reg a2t [jfrom:jto]; 
  reg a3t [7:0]; 
  reg a4t [0:7]; 

  // tmrg do_not_triplicate a1 a2 a3 a4
  wire a1;
  wire a2;
  wire a3;
  wire a4;
  assign a1=a1t[ito];
  assign a2=a2t[jfrom];
  assign a3=a3t[3];
  assign a4=a4t[3];

  //////////////////////////////////////////////////////////////////////////////
  // triplicated array = non triplicated array
  //////////////////////////////////////////////////////////////////////////////

  reg b1t;
  reg b2t; 
  reg b3t; 
  reg b4t; 

  // tmrg do_not_triplicate b1 b2 b3 b4
  wire b1 [ifrom:ito];
  wire b2 [jfrom:jto]; 
  wire b3 [7:0]; 
  wire b4 [0:7]; 
  always @*
    begin
      b1t=b1[ito];
      b2t=b2[jfrom];
      b3t=b3[4];
      b4t=b4[4];
    end

  // tmrg triplicate tmptri
  // tmrg do_not_triplicate tmp
  reg [0: 15-1] tmp;
  wire [0: 15-1] tmptri=tmp;
endmodule
