module a(
    input x,
    output y
);
    assign y = x;
    //  tmrg do_not_triplicate y
    // tmrg tmr_error true
endmodule
