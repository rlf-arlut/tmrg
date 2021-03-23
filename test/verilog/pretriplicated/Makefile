topTMR.v: top.v dividerTMR.v
	tmrg -v top.v -l dividerTMR.v

dividerTMR.v: divider.v
	tmrg $?

modulebTMR.v: moduleb.v moduleaTMR.v
	tmrg moduleb.v -l moduleaTMR.v -v

moduleaTMR.v:  modulea.v
	tmrg $?

clean:
	rm *TMR.v
