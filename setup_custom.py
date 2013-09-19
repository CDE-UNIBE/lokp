from setuptools import setup

setup(name='LMKP_Customization',
    packages=[],
    message_extractors = {
        'lmkp/customization': [
            ('sample/**', 'ignore', None),
            ('default/**', 'ignore', None),
            ('**.mak', 'mako', None),
        ]
    }
)
