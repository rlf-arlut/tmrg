################################################################################
#  Author: Szymon Kulis
#  This script is heaviliy based on THE RECIPE by Sandro Bonacini
################################################################################

if {[catch {

  # private namespace "ec" to prevent name clash
  namespace eval ec {}

  # start timer
  puts "Start at: [clock format [clock seconds] -format {%x %X}]"
  set ec::start [clock seconds]

  # Setup file, directories, and variables
  set ec::workDir         ${workDir}
  set ec::RTL_PATH        .
  set ec::VERILOG_LIST    { ${rtlFiles} }
  set ec::SDC             ${sdcFile}

  set ec::SYN_EFFORT      medium
  set ec::MAP_EFFORT      high
  set ec::INCR_EFFORT     high

  set TSMC_PDK $$env(TSMC_PDK)

  set DFT OFF

  set ec::LIB_PATH  "$$TSMC_PDK"

  set ec::LIBRARY   "$$TSMC_PDK/../../digital/Front_End/timing_power_noise/NLDM/tcbn65lp_200a/tcbn65lpwc.lib \
                     $$TSMC_PDK/../../digital/Front_End/timing_power_noise/NLDM/tpdn65lpnv2od3_200a/tpdn65lpnv2od3wc.lib \
                     $$TSMC_PDK/../../digital/Front_End/timing_power_noise/NLDM/tpan65lpnv2od3_200a/tpan65lpnv2od3wc.lib"


  set ec::VERILOG_VERSION 2001
  set ec::VHDL_LIST       {}
  set ec::VHDL_VERSION    1993

  set ec::LEFLIB    "$$TSMC_PDK/../../digital/Back_End/lef/tcbn65lp_200a/lef/tcbn65lp_6lmT1.lef \
                     $$TSMC_PDK/../../digital/Back_End/lef/tpdn65lpnv2od3_140b/mt_2/6lm/lef/tpdn65lpnv2od3_6lm.lef"
         
  set ec::CAPTABLE "$$TSMC_PDK/../../digital/Back_End/lef/tcbn65lp_200a/techfiles/captable/cln65lp_1p06m+alrdl_top1_cworst.captable"

  set ec::SUPPRESS_MSG    {LBR-30 LBR-31 VLOGPT-35}

  # include needed script
  include load_etc.tcl 


  # Preset global variables and attributes

  # define diagnostic variables
  set iopt_stats 1
  set global_map_report 1
  set map_fancy_names 1
  set path_disable_priority 0
  set crr_max_tries 300  ; # higher the number, more iterations: not much runtime penalty

  # define tool setup and compatibility
  set_attribute information_level 9 /  ; # valid range: 1 (least verbose) through 9 (most verbose)
  set_attribute hdl_max_loop_limit 1024 /
  set_attribute hdl_reg_naming_style %s_reg%s /
  set_attribute gen_module_prefix G2C_DP_ /
  # set_attribute endpoint_slack_opto 1 /
  #set_attribute optimize_constant_0_flops false /
  #set_attribute optimize_constant_1_flops false /
  set_attribute input_pragma_keyword {cadence synopsys get2chip g2c} /
  set_attribute synthesis_off_command translate_off /
  set_attribute synthesis_on_command translate_on /
  set_attribute input_case_cover_pragma {full_case} /
  set_attribute input_case_decode_pragma {parallel_case} /
  set_attribute input_synchro_reset_pragma sync_set_reset /
  set_attribute input_synchro_reset_blk_pragma sync_set_reset_local /
  set_attribute input_asynchro_reset_pragma async_set_reset /
  set_attribute input_asynchro_reset_blk_pragma async_set_reset_local /
  #set_attribute delayed_pragma_commands_interpreter dc /
  set_attribute script_begin dc_script_begin /
  set_attribute script_end dc_script_end /
  set_attribute iopt_force_constant_removal true /

  # triplication TMR persistence:
  #set_attribute merge_combinational_hier_instance false / 

  # suppress messages
  suppress_messages $$ec::SUPPRESS_MSG

  # setup shrink_factor attribute
  set_attribute shrink_factor 1.0 /

  # RTL and libraries setup

  # search paths
  set_attribute hdl_search_path $$ec::RTL_PATH /
  set_attribute lib_search_path $$ec::LIB_PATH /

  # timing libraries
  create_library_domain {sc9t }
  set_attribute library $$ec::LIBRARY sc9t
  set_attribute default true sc9t

  # lef & captbl
  set_attribute lef_library $$ec::LEFLIB /
  set_attribute cap_table_file $$ec::CAPTABLE /

  set_attribute interconnect_mode ple / 

  # report time and memory
  puts "\nEC INFO: Total cpu-time and memory after SETUP: [get_attr runtime /] sec., [get_attr memory_usage /] MBytes.\n"

  ### Power root attributes
  set_attribute lp_insert_clock_gating false /
  set_attribute lp_clock_gating_prefix lpg /
  set_attribute lp_insert_operand_isolation true /
  set_attribute hdl_track_filename_row_col true /

  # Load RTL
  set_attribute auto_ungroup none /
  set_attribute hdl_language sv /
  set_attribute hdl_infer_unresolved_from_logic_abstract true
  read_hdl $$ec::VERILOG_LIST

  # report time and memory
  puts "\nEC INFO: Total cpu-time and memory after LOAD: [get_attr runtime /] sec., [get_attr memory_usage /] MBytes.\n"

  # Elaborate
  elaborate

  # report time and memory
  puts "\nEC INFO: Total cpu-time and memory after ELAB: [get_attr runtime /] sec., [get_attr memory_usage /] MBytes.\n"

  # Constraint setup

  # read sdc constraint
  foreach ec::FILE_NAME $$ec::SDC {
    read_sdc $$ec::FILE_NAME
  }

  # report time and memory
  puts "\nEC INFO: Total cpu-time and memory after CONSTRAINT: [get_attr runtime /] sec., [get_attr memory_usage /] MBytes.\n"

  # Initial reports

  # print out the exceptions
  set ec::XCEP [find /designs* -exception *]
  puts "\nEC INFO: Total numbers of exceptions: [llength $$ec::XCEP]\n"
  catch {open $$ec::workDir/exception.all "w"} ec::FXCEP
  puts $$ec::FXCEP "Total numbers of exceptions: [llength $$ec::XCEP]\n"
  foreach ec::X $$ec::XCEP {
    puts $$ec::FXCEP $$ec::X
  }
  close $$ec::FXCEP

  # report time and memory
  puts "\nEC INFO: Total cpu-time and memory after POST-SDC: [get_attr runtime /] sec., [get_attr memory_usage /] MBytes.\n"

  # report initial design
  report design > $$ec::workDir/init.design

  # report initial gates
  report gates > $$ec::workDir/init.gate

  # report initial area
  report area > $$ec::workDir/init.area

  # report initial timing
  report timing -full > $$ec::workDir/init.timing


  # report initial summary
  puts "\nEC INFO: Reporting Initial QoR below...\n"
  redirect -tee $$ec::workDir/init.qor {report qor}
  
  puts "\nEC INFO: Reporting Initial Summary below...\n"
  redirect -tee $$ec::workDir/init.summary {report summary}

  report timing -lint

  # DFT
  set ec::DESIGN [find * -design *]

  # Leakage/Dynamic power/Clock Gating setup

  set_attribute max_leakage_power 0.0 "$$ec::DESIGN"

  # synthesize -to_generic -effort $$ec::SYN_EFFORT
  set_attribute remove_assigns true /
  set_remove_assign_options -verbose

  synthesize -to_generic -effort $$ec::SYN_EFFORT
  report datapath > $$ec::workDir/datapath_generic.rpt

  # Synthesizing to gates

  synthesize -to_mapped -eff $$ec::MAP_EFFORT -no_incr
  puts "Runtime & Memory after 'synthesize -to_map -no_incr'"
  report datapath > $$ec::workDir/datapath_mapped.rpt


  # Incremental Synthesis
  set incremental_opto 1

  synthesize -to_mapped -eff $$ec::INCR_EFFORT -incr   
  puts "Runtime & Memory after incremental synthesis"
  timestat INCREMENTAL

  foreach cg [find / -cost_group -null_ok *] {
    report timing -cost_group [list $$cg] > $$ec::workDir/[basename $$cg]_post_incr.rpt
  }


  # report time and memory
  puts "\nEC INFO: Total cpu-time and memory after SYN2GEN: [get_attr runtime /] sec., [get_attr memory_usage /] MBytes.\n"

  # report syn-to-generic design
  report design > $$ec::workDir/syn2gen.design

  # report syn-to-generic gates
  report gates > $$ec::workDir/syn2gen.gate

  # report syn-to-generic area
  report area > $$ec::workDir/syn2gen.area

  # report syn-to-generic timing
  report timing -full > $$ec::workDir/syn2gen.timing


  ### Create reports
  report clock_gating > $$ec::workDir/clockgating.rpt
  report power -depth 0 > $$ec::workDir/power.rpt
  report gates -power > $$ec::workDir/gates_power.rpt
  report operand_isolation > $$ec::workDir/op_isolation.rpt
  report area > $$ec::workDir/area.rpt
  report gates > $$ec::workDir/gates.rpt

  # Export sdf files
  #write_sdf -edges check_edge -delimiter "/" > $$ec::outDir/r2g.sdf

  # Convert sdf file to match IBM verilog gate models
  #exec sed s/RECOVERY/SETUP/ $$ec::outDir/r2g.sdf > $$ec::outDir/r2g_sim.sdf

  # Write the netlist
  write -m > $$ec::workDir/r2g.v

  # Write SDC file
  #write_sdc > $$ec::outDir/r2g.sdc

  # Write RC script file
  #write_script > $$ec::outDir/r2g.g

  # Write LEC file
  #write_do_lec -no_exit -revised_design $$ec::outDir/r2g.v -logfile syn_lec.log > $$ec::lecDir/rtl2map.tcl

  report timing -full

  # end timer
  puts "\nEC INFO: End at: [clock format [clock seconds] -format {%x %X}]"
  set ec::end [clock seconds]
  set ec::seconds [expr $$ec::end - $$ec::start]
  puts "\nEC INFO: Elapsed-time: $$ec::seconds seconds\n"

  # done
  ${exit}

  
} msg]} {
  puts "\nEC ERROR: RC could not finish successfully. Force an exit now. ($$msg)\n"
  exit -822
}

