test:
	flake8 audio_degrader
	flake8 tests
	python -m pytest tests -vv

package:
	python setup.py sdist
	python setup.py bdist_wheel
	twine upload dist/*

clean:
	rm -rf build dist audio_degrader.egg-info build
