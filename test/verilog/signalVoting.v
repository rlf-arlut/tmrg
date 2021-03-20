module sub (input a, output b);
    // tmrg do_not_touch
    assign b = a;
endmodule

module top();
    // tmrg default triplicate
    // tmrg do_not_triplicate sub_inst_a sub_inst_b

    wire conn; // connects output from instance A to input of instance B
    sub sub_inst_a (.a(), .b(conn));
    sub sub_inst_b (.a(conn), .b());
endmodule

