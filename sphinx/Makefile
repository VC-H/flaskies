# Makefile for Sphinx documentation
SPHINXBUILD   = python -msphinx
BUILDDIR      = _build

all:
	@echo
	@echo "target options:"
	@echo
	@grep "^\S*:" ./Makefile | sed -e "s/^\(.*\):\(.*\)$$/  \1:\2/g"
	@echo

packages_flaskies.png:
	( cd .. ; make uml )

html: packages_flaskies.png
	$(SPHINXBUILD) -b html -d $(BUILDDIR)/doctrees . $(BUILDDIR)/html

clean:
	rm -rf *~ $(BUILDDIR)/*
	rm -f packages_flaskies.png
