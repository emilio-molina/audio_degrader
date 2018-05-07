from setuptools import setup

setup(
    name='audio_degrader',
    packages=['audio_degrader'],
    version='1.0.5',
    description='Tool to introduce controlled degradations to audio',
    author='Emilio Molina',
    author_email='emilio.mol.mar@gmail.com',
    url='https://github.com/EliosMolina/audio_degrader',
    download_url='https://github.com/EliosMolina/audio_degrader/archive/master.zip',
    keywords=['audio', 'degradation', 'augmentation'],
    install_requires=['librosa >= 0.6.0'],
    package_data={'audio_degrader': ['resources/impulse_responses/*',
                                     'resources/sounds/*']},
    scripts=['scripts/audio_degrader'],
    include_package_data=True
)
