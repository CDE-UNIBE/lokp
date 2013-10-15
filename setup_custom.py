from setuptools import setup

setup(name='LMKP_Customization',
    packages=[],
    message_extractors = {
        'lmkp/customization': [
            ('sample/**', 'ignore', None),
            ('default/**', 'ignore', None),
            # Uncomment the customization you'd like to translate
#            ('lo/**', 'ignore', None),
#            ('spm/**', 'ignore', None),
#            ('testing/**', 'ignore', None),
            ('**.mak', 'mako', None),
        ]
    }
)
