module generate_test;
    genvar i;
    wire [7:0] test;
    generate
        for (i = 0; i < 3; i = i + 1) begin
            assign test[i] = 1'b1;
        end

        for (i = 3; i < 8; i = i + 1) begin
            assign test[i] = 1'b1;
        end
    endgenerate
endmodule
