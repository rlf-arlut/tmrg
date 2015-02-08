char function();
char (*fnptr)();

fnptr = function;

//then call the function with

ch = (*fnptr)(i);
