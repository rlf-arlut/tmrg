void printer(),textscreen(),windows();

switch (choice)
   {
   case 1: fnptr = printer;
           break;
   case 2: fnptr = textscreen;
        break;
   case 3: fnptr = windows;
   }

output(data,fnptr);
