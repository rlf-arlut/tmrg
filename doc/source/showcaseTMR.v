[...]
localparam  k=8;
wor dataTmrError;
wire [k-1:0] data [ 2*k-1 : 0 ] ;
wor selTmrError;
wire [2:0] sel;
reg  [2:0] selA;
reg  [2:0] selB;
reg  [2:0] selC;
reg  [k-1:0] dataA [ 2*k-1 : 0 ] ;
reg  [k-1:0] dataB [ 2*k-1 : 0 ] ;
reg  [k-1:0] dataC [ 2*k-1 : 0 ] ;
wire [k-1:0] dataMux =  data[sel] ;

majorityVoter #(.WIDTH(3)) selVoter (
    .inA(selA),
    .inB(selB),
    .inC(selC),
    .out(sel),
    .tmrErr(selTmrError)
    );

genvar gen_dataVoter;
generate
  for(gen_dataVoter =  ((0>2*k-1) ? 2*k-1 : 0);gen_dataVoter<((0>2*k-1) ? 0 : 2*k-1);gen_dataVoter =  gen_dataVoter+1)
    begin : gen_dataVoter_fanout 

      majorityVoter #(.WIDTH(((k-1)>(0)) ? ((k-1)-(0)+1) : ((0)-(k-1)+1))) dataVoter (
          .inA(dataA[gen_dataVoter] ),
          .inB(dataB[gen_dataVoter] ),
          .inC(dataC[gen_dataVoter] ),
          .out(data[gen_dataVoter] ),
          .tmrErr(dataTmrError)
          );
    end
endgenerate
[...]
