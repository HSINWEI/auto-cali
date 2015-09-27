from distutils.core import setup
import py2exe

excludes = ['Tkinter',
            'Tkconstants',
            ]

includes = [
#             "scipy.linalg.cython_blas",
#             "scipy.linalg.cython_lapack",
#             "scipy.special._ufuncs_cxx",
#             "scipy.integrate",
#             "scipy.interpolate.dfitpack",
#             "scipy.sparse.csgraph._validation",
            ]

dll_excludes=['w9xpopen.exe']

opts = {
    "py2exe": {
        "includes":includes,
        "excludes":excludes,
        'dll_excludes':dll_excludes,
        'bundle_files': 1,
        'compressed': True,
        'optimize': 2
    }
}
setup(console=['auto-cali.py'], 
      options=opts,
      zipfile = None)