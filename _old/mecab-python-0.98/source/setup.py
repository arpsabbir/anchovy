#!/usr/bin/env python

from distutils.core import setup,Extension,os
import string

setup(name = "mecab-python",
	version = '0.98',
	py_modules=["MeCab"],
	ext_modules = [
		Extension("_MeCab",
			["MeCab_wrap.cxx",],
			include_dirs=[r'C:\Develop\Mecab\sdk'],
			library_dirs=[r'C:\Develop\Mecab\sdk'],
			libraries=['libmecab'])
			])
