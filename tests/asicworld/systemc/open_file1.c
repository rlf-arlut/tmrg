char username[9];  /* One extra for nul char. */
int score;

...

while (fscanf(ifp, "%s %d", username, &score) != EOF) {
  fprintf(ofp, "%s %d\n", username, score+10);
}

...
