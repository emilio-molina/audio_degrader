from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='audio_degrader',
    packages=['audio_degrader'],
    version='1.3.0',
    description='Tool to introduce controlled degradations to audio',
    author='Emilio Molina',
    author_email='emilio.mol.mar@gmail.com',
    url='https://github.com/EliosMolina/audio_degrader',
    download_url='https://github.com/EliosMolina/audio_degrader/archive/master.zip',
    keywords=['audio', 'degradation', 'augmentation'],
    install_requires=install_requires,
    package_data={'audio_degrader': ['resources/impulse_responses/*',
                                     'resources/sounds/*']},
    scripts=['scripts/audio_degrader'],
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
