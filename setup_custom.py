from setuptools import setup

setup(name='LMKP_Customization',
    packages=[],
    message_extractors = {
        'lmkp/customization': [
            ('sample/**', 'ignore', None),
            ('default/**', 'ignore', None),
            # Uncomment or add the customization you'd like to ignore
#            ('lo/**', 'ignore', None),
#            ('spm/**', 'ignore', None),
#            ('testing/**', 'ignore', None),
            ('**.mak', 'mako', None),
        ]
    }
)
