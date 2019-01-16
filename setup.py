from setuptools import setup

with open('README.md',encoding='utf8') as fp:
    long_description = fp.read()

setup(
    name='cuecut',
    version='1.0.3',
    description='Cut a CD image file by its cue file',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Hu Zheyang',
    author_email='i@huzheyang.com',
    url='https://github.com/jsjyhzy/cuecut',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    python_requires='>=3',
    install_requires=[
        "CueParser==1.0.0",
        "chardet>=3.0.0",
    ],
    py_modules=['cuecut'],
    entry_points={
        'console_scripts': [
            'cuecut=cuecut:entrypoint',
        ],
    },
)
