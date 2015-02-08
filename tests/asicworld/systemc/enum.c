#include <stdio.h>

enum boolean {FALSE=0, TRUE };
enum months  {Jan=5, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec};
 
void main() {
  enum months month;
  enum boolean mybool;
  printf("Month %d\n", month=Aug);
  printf("Bool %d\n", mybool=TRUE);
}
