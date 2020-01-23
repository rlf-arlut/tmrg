module b(output error);
    // tmrg tmr_error true

    wire f;
    wire g;
    wire tmrError=1'b0;

    assign error = tmrError;
    a a (.x(f), .y(g));

endmodule

