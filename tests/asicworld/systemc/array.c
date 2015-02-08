#define SIZE 3

void main() {
  float x[SIZE];
  float *fp;
  int   i;
  // initialize the array x use a "cast" to force i into the equivalent float  
  for (i = 0; i < SIZE; i++) {
      x[i] = 0.5*(float)i;
  }
  for (i = 0; i < SIZE; i++) {
      printf("  %d  %f \n", i, x[i]);
  }
  // make fp point to array x     
  fp = x;
  // print via pointer arithmetic members of x are adjacent to   
  // each other in memory *(fp+i) refers to content of	  
  // memory location (fp+i) or x[i] 
  for (i = 0; i < SIZE; i++) {
      printf("  %d  %f \n", i, *(fp+i));
  }
}
