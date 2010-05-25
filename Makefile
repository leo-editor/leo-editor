rpm: MANIFEST
	python ./setup.py bdist --format=rpm

MANIFEST: bzr-manifest.txt
	for f in $$(sed -e 's/\r//' bzr-manifest.txt); do [ -f $$f ] && echo $$f; done > MANIFEST
