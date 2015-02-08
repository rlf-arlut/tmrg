#include "acc_user.h"
#include "veriuser.h"
#include "string.h"
#include "stdio.h"

#define IDLE      0
#define INCR      1
#define WAIT      2
#define DRIVE     3
#define DONE      4 

struct testGenObject {
  char* testFile;
  int   debug;
  char  cmdArray[100] [100];
  int   cmdSize;
  int   CmdPointer; 
  char* command;
  int   wait;
  int   value;
  int   clkCnt;
  int   state;
  handle count;
  handle enable;
  handle reset;
  handle clk;
  char* clk_value;
  char  *clk_last_value;
};

static struct testGenObject *object;

// Increment counter
void waitTicks () {
  object->clkCnt = object->clkCnt + 1;
}

// This function loads the content of test file into
// object command array
void loadTest() {
  FILE *testFile;
  char currentLine [100];
  object->cmdSize = 0;
  if((testFile = fopen(object->testFile, "r")) == NULL) {
     printf("Error Opening File.\n");
  }
  while (fgets(currentLine, sizeof(currentLine), testFile) != NULL ) {
    // Store the line cmdArray
    strcpy(object->cmdArray[object->cmdSize], currentLine);
    // print the line number and data
    if (object->debug) 
      printf("Line %d: %s\n", object->cmdSize, 
          object->cmdArray[object->cmdSize]);
    // Get each line from the test file 
    object->cmdSize ++;
  }
  // Close the test file 
  fclose(testFile);  
}

// This function process command line options
void processCmdOptions () {
  // Get debug option
  if (mc_scan_plusargs("plidebug") != NULL) {
     object->debug = 1;
  } else {
     object->debug = 0;
  }
  // Get test file name
  if (mc_scan_plusargs("test=") == NULL) {
    printf("ERROR : No test file option passed, use +test=testfile\n");
  } else {
    object->testFile =  mc_scan_plusargs("test=");
    if (object->debug) printf("Test file name %s\n",object->testFile);
  }
}

void doTest() {
  char* ptoks;
  char* tcmd;
  s_setval_delay delay_s;
  s_setval_value value_s;
  // Get current clock value
  object->clk_value =   acc_fetch_value(object->clk, "%b", 0);
  // BFM drives only at rising edge of clock
  if (!strcmp(object->clk_last_value,"1") && !strcmp(object->clk_value,"0")) {
    switch (object->state) {
      case IDLE  : 
        if (object->debug) printf("%d Current state is IDLE\n", tf_gettime());
        if (object->CmdPointer < object->cmdSize) {
          tcmd = object->cmdArray[object->CmdPointer];
          if (object->debug) printf ("Test line %d current command-%s",
              object->CmdPointer, tcmd);
          ptoks = strtok(tcmd, ":");
          int lcnt = 0;
          while(ptoks != NULL) {
            if (*ptoks != '=') {
              if (lcnt == 0) {
                object->wait = atoi(ptoks);
                if (object->debug) printf("Wait    : %d\n", object->wait);
              } else if (lcnt == 1) {
                object->command = ptoks;
                if (object->debug) printf("Command : %s\n", ptoks);
              } else {
                object->value = atoi(ptoks);
                if (object->debug) printf("Value   : %d\n", object->value);
              }
              lcnt ++;
            }
            ptoks = strtok(NULL, " ");
          }
          object->CmdPointer ++ ;
          if (object->wait == 0) {
            if (object->debug) printf("%d Next State DRIVE\n", tf_gettime());
            object->state = DRIVE;
            doTest();
          } else {
            if (object->debug) printf("%d Next State WAIT\n", tf_gettime());
            object->state = WAIT;
          }
        } else {
          if (object->debug) printf("%d Next State DONE\n", tf_gettime());
          object->state = DONE;
        }
        break;
      case WAIT  : 
          if (object->debug) printf("%d Current state is WAIT : %d\n", 
              tf_gettime(), object->clkCnt);
          if ((object->clkCnt + 1) >= object->wait) {
            object->wait = 0;
            object->clkCnt = 0;
            if (object->debug) printf("%d Next State DRIVE\n", tf_gettime());
            object->state = DRIVE;
            doTest();
          } else {
            waitTicks();
          }
          break;
      case DRIVE : 
         if (object->debug) printf("%d Current state is DRIVE\n", tf_gettime());
         value_s.format    = accIntVal;
         delay_s.model     = accNoDelay; 
         delay_s.time.type = accTime;
         delay_s.time.low  = 0;
         delay_s.time.high = 0;
         if (!strcmp(object->command,"reset")) {
           value_s.value.integer =  object->value;
           acc_set_value(object->reset,&value_s,&delay_s);
         } else if (!strcmp(object->command,"enable")) {
           value_s.value.integer =  object->value;
           acc_set_value(object->enable,&value_s,&delay_s);
         } else {
           if (object->debug) printf("ERROR : What command do you want\n");
         }
         if (object->debug) printf("%d Next State IDLE\n", tf_gettime());
         object->state = IDLE;
         break;
      case DONE  : 
         if (object->debug) printf("%d Current state is DONE\n", tf_gettime());
         tf_dofinish(); 
         break;
      default    : object->state = IDLE;
                   break;
    }
  }
  object->clk_last_value =   acc_fetch_value(object->clk, "%b", 0);
}

void initCounterTestGen () {
  //acc_initialize( ); 
  //acc_configure( accDisplayErrors, "false" );
  object = (struct testGenObject *) malloc (sizeof(struct testGenObject));
  // Load the initial and defaule values
  object->testFile = "simple.tst";
  object->cmdSize = 0;
  object->CmdPointer = 0;
  object->clkCnt = 0;
  object->state = IDLE;
  // Initialize this instance of the model.
  object->clk    = acc_handle_tfarg(1);
  object->reset  = acc_handle_tfarg(2);
  object->enable = acc_handle_tfarg(3);
  object->count  = acc_handle_tfarg(4);
  // Drive inactive signals on all inputs
  tf_putp (2, 0);
  tf_putp (3, 0);
  // Save a copy of the present clk value.
  object->clk_last_value =   acc_fetch_value(object->clk, "%b", 0);
  // Get the command line testfile name and debug option
  processCmdOptions();
  // Open the testfile and make array of command
  loadTest(object);
  // Add callback when ever clock changes
  acc_vcl_add( object->clk, doTest, object->clk_value, vcl_verilog_logic );
  // All acc routines should have this
  acc_close();
}
