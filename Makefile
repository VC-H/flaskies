all:
	@echo
	@echo "target options:"
	@echo
	@grep "^\S*:" ./Makefile | sed -e "s/^\(.*\):.*$$/  \1/g"
	@echo

ls:
	find . \! -regex '.*\/\.git\/.*'

coverage:
	python -m coverage erase && \
	python -m coverage run testall.py && \
	python -m coverage report -m

uml:
	pyreverse -o png -p flaskies --ignore=testall.py,tmp .
	\rm -f classes_flaskies.png
	\mv -f packages_flaskies.png sphinx/

html:
	( cd sphinx; make html )

clean:
	find . -name '__pycache__' -exec \rm -rf {} +
	find . -name '*.pyc' -exec \rm -f {} +
	find . -name '*.pyo' -exec \rm -f {} +
	find . -name '*~' -exec \rm -f {} +
	( cd sphinx; make clean )
