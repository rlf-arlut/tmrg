module assigment02;
        // tmrg default triplicate
        reg  [15:0] inbuffer;
        wire  [15:0] inbuffer_mux;
        wire [15:0] inbufferVoted               = inbuffer;
        assign inbuffer_mux =    (PhaseShift == 0)? {inbufferVoted[6:0],in}:
                                  ((PhaseShift == 1)? inbufferVoted[7:0]:
                                   ((PhaseShift == 2)? inbufferVoted[8:1]:
                                    ((PhaseShift == 3)? inbufferVoted[9:2]:
                                     ((PhaseShift == 4)? inbufferVoted[10:3]:
                                      ((PhaseShift == 5)? inbufferVoted[11:4]:
                                       ((PhaseShift == 6)? inbufferVoted[12:5]:       
                                        ((PhaseShift == 7)? inbufferVoted[13:6]:7'd0)))))));
endmodule
