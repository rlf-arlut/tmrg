// comment
module test01( 
  input in0,
  input in1,
  input in2,
  input in3,
  output out0,
  output out1,
  output out2,
  output out3,
  output out4,
  output out5,
  output out6,
  output out7,
  output out8,
  output out9,
  output out10,
  output out11,
  output out12,
  output [1:0] out13,
  output [1:0] out14,
  output out15,
  output out16,
  output out17,
  output out18
);
  assign 
    out0=in1 & in2, //bit-wise AND operator
    out1=&in1, //unary reduction AND operator
    out2=in1 && in2, //logical AND operator
    out3=~&in1, //unary reduction NAND operator
    out4=in1 | in2, //bit-wise OR operator
    out5=in1 || in2, //logical OR operator
    out6=|in1, //unary reduction OR operator
    out7=~|in1, //unary reduction NOR operator
    out8=in1 ^ in2, //bit-wise XOR operator
    out9=^in1,//unary reduction XNOR operator
    out10=~^in1,//unary reduction XNOR operator
    out11=~in1,//bit-wise NOT operator
    out12 = !in1,//logical NOT operator
    out13={in1,in2},//concatenation operator
    out14={2{in1}},//duplicate concatenation operator
    out15=in0 ? in1 : in2,//conditional operator
    out17= in1 == in2,//logical equality operator
    out18= in1 != in2;//logical inequality operator

endmodule
