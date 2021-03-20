module submodule (
    input a,
    output b
);
    // tmrg tmr_error true
    wire aVoted = a;
    assign b = a;
endmodule

module topmodule (
    input a,
    output b
);
    submodule submodule_inst (.a(a), .b(b));
endmodule


