struct conditions {
  float temp;
  union feels_like {
    float wind_chill;
    float heat_index;
  }
} today;
