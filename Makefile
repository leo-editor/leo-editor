# Base the rpm release number on the number of bzr revisions since formal
# release.  3012 was the revision for 4.7.1 as tagged in bzr.
rpm: MANIFEST
	echo '[bdist_rpm]'>setup.cfg
	echo 'release='$$((`bzr revno` - 3012))>>setup.cfg
	python ./setup.py bdist --format=rpm

MANIFEST: bzr-manifest.txt
	for f in $$(sed -e 's/\r//' bzr-manifest.txt); do [ -f $$f ] && echo $$f; done > MANIFEST
