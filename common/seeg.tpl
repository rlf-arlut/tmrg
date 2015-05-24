// - Single Event Transient - - - - - - - - - - - - - - - - - - - - - - - - - -
task set_force_net;
  input wireid;
  integer wireid;
  begin
    case (wireid)
${set_force_net}
    endcase
  end
endtask

task set_release_net;
  input wireid;
  integer wireid;
  begin
    case (wireid)
${set_release_net}
    endcase
  end
endtask

task set_display_net;
  input wireid;
  integer wireid;
  begin
    case (wireid)
${set_display_net}
    endcase
  end
endtask

task set_max_net;
  output wireid;
  integer wireid;
  begin
    wireid=${set_max_net};
  end
endtask

// - Single Event Upset - - - - - - - - - - - - - - - - - - - - - - - - - - - -

task seu_force_net;
  input wireid;
  integer wireid;
  begin
    case (wireid)
${seu_force_net}
    endcase
  end
endtask

task seu_release_net;
  input wireid;
  integer wireid;
  begin
    case (wireid)
${seu_release_net}
    endcase
  end
endtask

task seu_display_net;
  input wireid;
  integer wireid;
  begin
    case (wireid)
${seu_display_net}
    endcase
  end
endtask

task seu_max_net;
  output wireid;
  integer wireid;
  begin
    wireid=${seu_max_net};
  end
endtask

// - Single Event Efect - - - - - - - - - - - - - - - - - - - - - - - - - - - -

task see_force_net;
  input wireid;
  integer wireid;
  begin
    if (wireid<${set_max_net})
      set_force_net(wireid);
    else
      seu_force_net(wireid-${set_max_net});
  end
endtask

task see_release_net;
  input wireid;
  integer wireid;
  begin
    if (wireid<${set_max_net})
      set_release_net(wireid);
    else
      seu_release_net(wireid-${set_max_net});
  end
endtask

task see_display_net;
  input wireid;
  integer wireid;
  begin
    if (wireid<${set_max_net})
      set_display_net(wireid);
    else
      seu_display_net(wireid-${set_max_net});
  end
endtask

task see_max_net;
  output wireid;
  integer wireid;
  begin
    wireid=(${set_max_net} + ${seu_max_net});
  end
endtask
