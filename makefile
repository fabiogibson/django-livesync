clean:
	@find . -name *.pyc -delete

test:
	@coverage run runtests.py
	@coverage html --include "./livesync/*"
