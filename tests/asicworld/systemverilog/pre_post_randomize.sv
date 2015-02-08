program pre_post_randomize;

  class frame_t;
    rand bit [7:0] data;
    bit  parity;
    constraint c {
     data >  0;
    }
    function void pre_randomize();
      begin
        $write("pre_randomize  : Value of data %b and parity %b\n",data,parity);
      end
    endfunction
    function void post_randomize();
      begin
        parity = ^data;
        $write("post_randomize : Value of data %b and parity %b\n",data,parity);
      end
    endfunction
   endclass

  initial begin
    frame_t frame = new();
    integer i = 0;
    $write("-------------------------------\n");
    $write("Randomize Value\n");
    $write("-------------------------------\n");
    i = frame.randomize();
    $write("-------------------------------\n");
  end
endprogram
