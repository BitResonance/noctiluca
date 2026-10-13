.PHONY: verify clean
verify:
	python3 scripts/verify_outputs.py

clean:
	$(MAKE) -C c clean
	rm -rf java/out rust/target swift/.build
