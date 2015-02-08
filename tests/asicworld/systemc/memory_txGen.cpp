#include "memory_txGen.h"

void memory_txGen::test() {
  scv_smart_ptr  <mem_t > object;
  int error = 0;
  // Drive low on all signals input to DUT
  addr  = 0;
  wr    = 0;
  cs    = 0;
  wdata = 0; 
  done  = 0;
  wait(1); // wait for one clock
  cout<<"@"<<sc_time_stamp()<<" Starting the memory write/read test"<<endl;
  for(int i = 0; i < 10;i++) {
    // Get the next random address and data object
    object->next();
    //------------------------------------------
    //  Do Memory Write
    //------------------------------------------
    // Drive the addess
    addr  = object->addr.read();
    // Drive the data
    wdata = object->data.read();
    // Drive Chip Select
    cs    = 1;
    // Drive write enable
    wr    = 1;
    cout<<"@"<<sc_time_stamp()<<" Writing address : "<< object->addr <<endl;
    wait(1); // Wait for one clock
    cs    = 0; // Deassert chip select
    wr    = 0; // Deassert write enable
    wait(1); // Wait for one clock
    //------------------------------------------
    //  Do Memory Read from Same Address
    //------------------------------------------
    cs    = 1; // Assert the chip select
    cout<<"@"<<sc_time_stamp()<<" Reading address : "<< object->addr <<endl;
    wait(1);
    // Compare the data written with read data
    if (rdata != wdata) {
      error ++; // If error increment counter
      cout<<"@"<<sc_time_stamp()<<" Error : Write data : " << 
        wdata << " Read data : " << rdata << endl;
    } else {
      cout<<"@"<<sc_time_stamp()<<" Match : Write data : " << 
        wdata << " Read data : " << rdata << endl;
    }
    cs    = 0; // Deassert the chip selct
    wait(1);
  }
  // Request for simulation termination
  if (error > 0) {
    cout << "=======================================" << endl;
    cout << " SIMULATION FAILED" << endl;
    cout << "=======================================" << endl;
  } else {
    cout << "=======================================" << endl;
    cout << " SIMULATION PASSED" << endl;
    cout << "=======================================" << endl;
  }
  done = 1;
  // Just wait for few cycles
  wait(100);
}
