test:
	flake8 audio_degrader
	flake8 tests
	python -m pytest tests -vv

package:
	# to upload package to pip repo
	python setup.py sdist
	python setup.py bdist_wheel
	twine upload dist/*  # user eelioss
	# for test repo:
	# twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	# pip install --index-url https://test.pypi.org/simple/ audio_degrader

clean:
	rm -rf build dist audio_degrader.egg-info build
