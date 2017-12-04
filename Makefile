all:
	@echo
	@echo "target options:"
	@echo
	@grep "^\S*:" ./Makefile | sed -e "s/^\(.*\):.*$$/  \1/g"
	@echo

ls:
	find . \! -regex '.*\/\.git\/.*'

clean:
	find . -name '__pycache__' -exec \rm -rf {} +
	find . -name '*.pyc' -exec \rm -f {} +
	find . -name '*.pyo' -exec \rm -f {} +
	find . -name '*~' -exec \rm -f {} +
