from setuptools import setup, find_packages

setup(
    name='audio_degrader',
    packages=['audio_degrader'],
    version='1.0.1',
    description='Tool to introduce controlled degradations to audio',
    author='Emilio Molina',
    author_email='emilio.mol.mar@gmail.com',
    url='https://github.com/EliosMolina/audio_degrader',
    download_url='https://github.com/EliosMolina/audio_degrader/archive/master.zip',
    keywords=['audio', 'degradation', 'augmentation'],
    install_requires=['numpy >= 1.14.3', 'librosa >= 0.6.0'],
    package_data={'audio_degrader': ['resources/impulse_responses/*',
                                     'resources/sounds/*']},
    include_package_data=True
)
