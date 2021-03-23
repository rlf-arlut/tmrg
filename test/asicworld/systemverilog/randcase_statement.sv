module randcase_statement;

 task do_randcase();
   begin
     randcase
       20 : begin
              $write ("What should I do ? \n");
            end
       20 : begin
              $write ("Should I work\n");
            end
       20 : begin
              $write ("Should I watch Movie\n");
            end
       40 : begin
              $write ("Should I complete tutorial\n");
            end
     endcase 
   end
 endtask

 initial begin
   repeat(10) begin
     // You need to run for more iteration to
     // get proper distribution
     do_randcase();
   end  
   $finish;
 end
endmodule
