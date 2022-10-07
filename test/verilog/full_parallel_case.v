module full_parallel_case ();

    reg foo, bar;

    always @* begin 
    (* full_case=1, parallel_case *)
        case (foo)
            1'b0: bar = 1'b0;
            1'b1: bar = 1'b1;
        endcase
    end

endmodule