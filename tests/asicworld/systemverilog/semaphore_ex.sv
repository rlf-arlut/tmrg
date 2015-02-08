program semaphore_ex;

  semaphore  semBus = new(1);

  initial begin
    fork 
      agent("AGENT 0",5);
      agent("AGENT 1",20);
    join
  end

  task automatic agent(string name, integer nwait);
    integer i = 0;
    for (i = 0 ; i < 4; i ++ ) begin
      semBus.get(1);
      $display("[%0d] Lock semBus for %s", $time,name);
      #(nwait);
      $display("[%0d] Release semBus for %s", $time,name);
      semBus.put(1);
      #(nwait);
    end
  endtask

endprogram
