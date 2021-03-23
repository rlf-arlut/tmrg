`timescale 1ns/100ps
module string_literals ();

string  a;

initial begin
  $display ("@ %gns a = %s", $time, a);
  a = "Hello Deepak";
  $display ("@ %gns a = %s", $time, a);
  #1 a = "Over writing old string";
  $display ("@ %gns a = %s", $time, a);
  #1 a = "This is multi line comment \
          and this is second line";
  $display ("@ %gns a = %s", $time, a);
  #1 $finish;
end

endmodule
