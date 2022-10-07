module parallel_full_case ();

    reg foo, bar;

    always @* begin 
    (* parallel_case, full_case=1 *)
        case (foo)
            1'b0: bar = 1'b0;
            1'b1: bar = 1'b1;
        endcase
    end

endmodule
