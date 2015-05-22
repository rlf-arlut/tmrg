   module dff(d,c,q);
     // tmrg default triplicate
     input d,c;
     output q;
     reg q;
     wire dVoted=d;
     always @(posedge c)
       q<=dVoted;
   endmodule
