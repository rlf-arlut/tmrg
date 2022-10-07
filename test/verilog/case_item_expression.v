module case_item_expression ();

    // tmrg default do_not_triplicate

    reg a;
    reg b, c;

    always @* begin
        case (1'b1)
            b && c: a = 1'b1;
            1'b0, 1'b1: a = 1'b1;
        endcase
    end

endmodule
