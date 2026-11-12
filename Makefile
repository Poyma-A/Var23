.PHONY: run test

run:
	python3 main.py $(ARGS)

test:
	python3 -m unittest discover \
	  -s tests
