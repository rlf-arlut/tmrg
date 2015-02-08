virtual function string get_name();
virtual function string get_instance();
virtual function void start_xactor();
virtual function void stop_xactor();
virtual function void reset_xactor(reset_e rst_typ = SOFT_RST);
virtual function void save_rng_state();
virtual function void restore_rng_state();
virtual function void xactor_status(string prefix = "");
virtual protected task main();
protected task wait_if_stopped();
protected task wait_if_stopped_or_empty(vmm_channel chan);
virtual function void prepend_callback(vmm_xactor_callbacks cb);
virtual function void append_callback(vmm_xactor_callbacks cb);
virtual function void unregister_callback(vmm_xactor_callbacks cb);
