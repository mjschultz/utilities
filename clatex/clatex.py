#!/usr/bin/env python

import os, sys, tempfile
import shutil, subprocess
import optparse

latex_path = '/usr/texbin/latex'
dvipng_path = '/usr/texbin/dvipng'
dvipng_args = ['-bg Transparent', "-fg 'rgb 0.0 0.0 0.0'",
               '-Ttight', '-D100']
base_name = 'clatex'

def create_source(content, size='normalsize') :
	source = '\documentclass[12pt]{article}'\
             '\usepackage{amsmath,amsfonts,amssymb}'\
             '\usepackage[mathscr]{eucal}'\
             '\pagestyle{empty}'
	source += '\\begin{document}'
	source += '\\begin{'+size+'}'
	source += '\\begin{math}'
	source += content
	source += '\end{math}'
	source += '\end{'+size+'}'
	source += '\end{document}'
	return source

def build_latex(latex_file) :
	cwd = os.path.dirname(latex_file)
	args = [latex_path, latex_file]
	subprocess.call(args, cwd=cwd)

def build_png(dvi_file) :
	cwd = os.path.dirname(dvi_file)
	png_file = base_name+'.png'
	args = [dvipng_path, dvi_file, '-o'+png_file] + dvipng_args
	subprocess.call(args, cwd=cwd)
	return cwd+'/'+png_file

def main(args) :
	op = optparse.OptionParser()
	op.add_option('-s', '--size', dest='size', default='normalsize',
					help='LaTeX size to produce')
	(options, args) = op.parse_args(args)

	# create a temporary staging directory
	tmpdir = tempfile.mkdtemp()
	base = tmpdir+'/'+base_name
	# generate the source based on the input
	source = create_source(args[1], options.size)
	latex_file = base+'.tex'
	f = open(latex_file, 'w')
	f.write(source)
	f.close()
	# build the latex into a dvi file
	build_latex(latex_file)
	# bump the dvi into a png
	dvi_file = base+'.dvi'
	png_file = build_png(dvi_file)
	shutil.copy(png_file, '.')
	shutil.rmtree(tmpdir)

if __name__ == '__main__' :
	main(sys.argv)
