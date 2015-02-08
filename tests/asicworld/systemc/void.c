#include <stdio.h>

void Print_Square(int Number);

void main ()
{
   Print_Square(5);
   exit(0);
}

void Print_Square(int Number)
{
   printf("%d squared is %d\n",Number, Number*Number);
}
