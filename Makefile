#-----------------------------------------------------------------------------
# Target: clean
#-----------------------------------------------------------------------------
.PHONY: clean
clean: ; $(info $(M) cleaning...)	@
	@rm -rf ./bin

#------------------------------------------------------
# Setup Targets
#------------------------------------------------------

prereqs: 											## Verify that required utilities are installed
	@echo -- $@ --

#------------------------------------------------------
# Run Targets
#------------------------------------------------------
run-2syn:
	sudo python3 -u ./algorithm/2syn_alg.py |tee ./bin/2syn_log.file
run-epsilon:
	sudo python3 -u ./algorithm/mab_alg.py -p EPSILON_GREEDY |tee ./bin/epsilon_greedy_log.file
run-ucb:
	sudo python3 -u ./algorithm//mab_alg.py -p UCB |tee ./bin/ucb_log.file
run-th-sampling:
	sudo python3 -u ./algorithm/mab_alg.py -p T_SAMPLING |tee ./bin/t_sampling_log.file
