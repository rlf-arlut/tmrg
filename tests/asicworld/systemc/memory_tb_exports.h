#ifndef MEMORY_TB_EXPORTS_H
#define MEMORY_TB_EXPORTS_H

#ifdef __cplusplus
extern "C" {
#endif

void init_sc     ();
void exit_sc     ();
void sample_hdl  (void *Invector);
void drive_hdl   (void *Outvector);
void advance_sim (unsigned long simtime);
void exec_sc     (void *invector, void *outvector, unsigned long simtime);

#ifdef __cplusplus
}
#endif

#endif
