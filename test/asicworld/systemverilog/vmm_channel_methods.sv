virtual void reconfigure(int full = -1, int empty = -1, 
  logic fill_as_bytes = 1'bx);
virtual int unsigned full_level();
virtual int unsigned empty_level();
virtual int unsigned level();
virtual int unsigned size();
virtual bit is_full();
function void flush();
function void sink();
function void flow();
function void lock(bit [1:0] who);
function void unlock(bit [1:0] who);
function bit is_locked(bit [1:0] who);
function void display(string prefix = "");
function string psdisplay(string prefix = "");
task put(vmm_data obj, int offset = -1);
function void sneak(vmm_data obj, int offset = -1);
function vmm_data unput(int offset = -1);
task get(output vmm_data obj, input int offset = 0);
task peek(output vmm_data obj, input int offset = 0);
task activate(output vmm_data obj, input int offset = 0);
function vmm_data active_slot();
function vmm_data start();
function vmm_data complete(vmm_data status = null);
function vmm_data remove();
function active_status_e status();
function bit tee_mode(bit is_on);
task tee(output vmm_data obj);
function void connect(vmm_channel downstream);
function vmm_data for_each(bit reset = 0);
function int unsigned for_each_offset();
function bit record(string filename);
task playback(output bit success, input string filename, 
  input vmm_data loader, input bit metered = 0);