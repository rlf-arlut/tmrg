program rand_mode_ex;
  class frame_t;
    rand bit [7:0] src_addr;
    rand bit [7:0] dst_addr;
    task print();
      begin 
        $write("Source      address %2x\n",src_addr);
        $write("Destination address %2x\n",dst_addr);
      end
    endtask  
  endclass

  initial begin
    frame_t frame = new();
    integer j = 0;
    $write("-------------------------------\n");
    $write("Without Randomize Value\n");
    frame.print();
    $write("-------------------------------\n");
    $write("With Randomize Value\n");
    j = frame.randomize();
    frame.print();
    $write("-------------------------------\n");
    $write("With Randomize OFF and Randomize\n");
    frame.rand_mode(0);
    j = frame.randomize();
    frame.print();
    $write("-------------------------------\n");
    $write("With Randomize ON and Randomize\n");
    frame.rand_mode(1);
    j = frame.randomize();
    frame.print();
    $write("-------------------------------\n");
    $write("With Randomize OFF on dest addr and Randomize\n");
    frame.dst_addr.rand_mode(0);
    j = frame.randomize();
    frame.print();
    $write("-------------------------------\n");
  end
endprogram
