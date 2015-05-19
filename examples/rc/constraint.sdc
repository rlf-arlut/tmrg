set sdc_version 1.3

set_load 0.001 [all_outputs]
set_max_fanout       100
set_max_transition   10 [current_design]
set_input_transition 10 [all_inputs]

set_dont_touch fanout
set_dont_touch /designs/comb03TMR/nets/inA
set_dont_touch /designs/comb03TMR/nets/inB
set_dont_touch /designs/comb03TMR/nets/inC
