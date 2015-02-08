#include "counter.h"

// Counter model
void counter::cnt_model() {
  while (true) {
    wait();
    if (rst.read()) {
      cnt = 0;
    } else {
      cnt ++;
    }
  }
}
// Counter montitor
void counter::monitor() {
  error = 0;
  while (true) {
    wait();
    cout << "@" <<sc_time_stamp() << "Counter Monitor : tb "
       << cnt << " dut " << d_out << endl;
    if (rst.read() == 0) {
       if (cnt != d_out) {
         error ++;
       }
    }
  }
}
// Counter stim gen
void counter::test() {
  done = 0;
  while (true) {
    rst = true;
    cout<<"@"<<sc_time_stamp()<<" Asserting Reset " << endl;
    wait(10);
    rst = false;
    cout<<"@"<<sc_time_stamp()<<" De-asserting Reset " << endl;
    wait(20);
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
}
