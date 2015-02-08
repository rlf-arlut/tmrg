`include "vmm.sv"

// Need to extend from base class vmm_xactor
class child extends vmm_xactor;
  vmm_log log;
  
  function new(vmm_log log,string name);
    super.new(name, "child");
    this.log = log;
  endfunction

  virtual task main();
    super.main();
    fork
      begin
        this.bfm();
      end
    join_none
  endtask

  task bfm();
    while(1) begin
      #10; // This can be clock event
      wait_if_stopped();
      `vmm_note(log,"Child is running");
    end
  endtask
endclass

// Need to extend from base class vmm_xactor
class parent extends vmm_xactor;
  vmm_log log;
  child   divya;
  
  function new(vmm_log log,string name);
    super.new(name, "parent");
    this.log = log;
    this.divya = new(log,name);
  endfunction

  virtual task main();
    super.main();
    fork
      begin
        this.bfm();
      end
      begin
        this.flow_ctrl();
      end
    join_none
  endtask

  virtual function void start_xactor();
    super.start_xactor();
    this.divya.start_xactor();
  endfunction

  virtual function void stop_xactor();
    super.stop_xactor();
    this.divya.stop_xactor();
  endfunction

  virtual function void reset_xactor(reset_e rst_typ = SOFT_RST);
    super.reset_xactor();
    this.divya.reset_xactor();
  endfunction

  virtual function void xactor_status(string prefix = "");
   super.xactor_status(prefix);
   this.divya.xactor_status(prefix);
  endfunction

  task bfm();
    while(1) begin
      #10; // This can be clock event
      wait_if_stopped();
      `vmm_note(log,"Parent bfm is running");
    end
  endtask

  task flow_ctrl();
    while(1) begin
      #10; // This can be clock event
      wait_if_stopped();
      `vmm_note(log,"Parent flow_ctrl is running");
    end
  endtask
endclass

program test();
  vmm_log log = new("test","test");
  parent  deepak    = new(log,"PROGRAM");
  initial begin
     $display("--------------------------------");
     $display(" Calling start_xactor");
     $display("--------------------------------");
     deepak.start_xactor();
     deepak.xactor_status("ASIC-WORLD ");
     #20;
     $display("--------------------------------");
     $display(" Calling stop_xactor");
     $display("--------------------------------");
     deepak.stop_xactor();
     deepak.xactor_status("ASIC-WORLD ");
     #100;
     $display("--------------------------------");
     $display(" Calling start_xactor");
     $display("--------------------------------");
     deepak.start_xactor();
     deepak.xactor_status("ASIC-WORLD ");
     #20;
     $display("--------------------------------");
     $display(" Calling reset_xactor");
     $display("--------------------------------");
     deepak.reset_xactor();
     deepak.xactor_status("ASIC-WORLD ");
     #40;
  end
endprogram
