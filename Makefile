test:
	python -m pytest tests -vv

package:
	python setup.py sdist
	python setup.py bdist_wheel
	twine upload dist/*

clean:
	rm -rf build dist audio_degrader.egg-info build