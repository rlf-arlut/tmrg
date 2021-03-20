program extend_methods;
 // Define the class
 class aop;
    integer i;
    integer j;
    integer k;
    function void print_i ();
      $display ("[1] Value of i %0d",i);
    endfunction
    function void print_j ();
      $display ("[1] Value of i %0d",j);
    endfunction
    function void print_k ();
      $display ("[1] Value of i %0d",k);
    endfunction

    function void print_i_j ();
      $display ("[1] Value of i %0d",i);
      $display ("[1] Value of i %0d",j);
    endfunction
 endclass
 // Add new variable j and method print2 to aop class
 extends aop_extend (aop);
    before function void print_i ();
      $display ("[2] Value of i %0d",i + 10);
    endfunction
    after function void print_j ();
      $display ("[2] Value of j %0d",j + 10);
    endfunction
    around function void print_k ();
      $display ("[2] Value of k %0d",k + 10);
    endfunction
    before function void print_i_j ();
      $display ("[2] Value of i %0d",i + 20);
    endfunction
    after function void print_i_j ();
      $display ("[2] Value of j %0d",j + 20);
    endfunction

 endextends
 // Create instance of the aop class
 aop a_;

 initial begin
   a_ = new ();
   a_.i = 10;
   a_.j = 11;
   a_.k = 11;
   a_.print_i(); 
   a_.print_j(); 
   a_.print_k(); 
   a_.print_i_j(); 
 end

endprogram
