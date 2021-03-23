//+++++++++++++++++++++++++++++++++++++++++++++++++
// Simple Program with ports
//+++++++++++++++++++++++++++++++++++++++++++++++++
program simple(input wire clk,output logic reset,
            enable, input logic [3:0] count);
  //=================================================
  // Initial block inside program block
  //=================================================
  initial begin
    $monitor("@%0dns count = %0d",$time,count);
    reset = 1;
    enable = 0;
    #20 reset = 0;
    @ (posedge clk);
    enable = 1;
    repeat (5) @ (posedge clk);
    enable = 0;
    // Call task in module
    simple_program.do_it();
  end
  //=================================================
  // Task inside a module
  //=================================================
  task do_it();
    $display("%m I am inside program");
  endtask

endprogram
//=================================================
//  Module which instanciates program block
//=================================================
module simple_program();
logic clk  = 0;
always #1 clk ++;
logic [3:0] count;
wire reset,enable;
//=================================================
// Simple up counter
//=================================================
always @ (posedge clk)
 if (reset) count <= 0;
 else if (enable) count ++;
//=================================================
// Program is connected like a module
//=================================================
simple prg_simple(clk,reset,enable,count);
//=================================================
// Task inside a module
//=================================================
task do_it();
  $display("%m I am inside module");
endtask
//=================================================
// Below code is illegal
//=================================================
//initial begin
//  prg_simple.do_it();
//end

endmodule
