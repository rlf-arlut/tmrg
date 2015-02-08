//+++++++++++++++++++++++++++++++++++++++++++++++++
// Simple Program with ports
//+++++++++++++++++++++++++++++++++++++++++++++++++
program exit_simple(input wire clk,output logic reset,
            enable, input logic [3:0] count);
  //=================================================
  // Initial block inside program block
  //=================================================
  initial begin
    $monitor("@%0dns count = %0d",$time,count);
    fork
       do_something();
    join_none
    reset = 1;
    enable = 0;
    #20 reset = 0;
    @ (posedge clk);
    enable = 1;
    repeat (5) @ (posedge clk);
    enable = 0;
    #10 $exit();
    #100 $display("%0dns Terminating simulation", $time);
    $finish;
  end
  //=================================================
  // Simple task
  //=================================================
  task do_something();
    while (1) begin
       #5 $display("%0dns inside do_something task", $time);
    end
  endtask

endprogram
//=================================================
//  Module which instanciates program block
//=================================================
module exit_program();
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
exit_simple prg_simple(clk,reset,enable,count);

endmodule
