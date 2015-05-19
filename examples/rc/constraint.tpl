set sdc_version 1.3

set_input_transition 10    [all_inputs]
set_load             0.001 [all_outputs]
set_max_fanout       100   [current_design]
set_max_transition   10    [current_design]

${dont_touch}
