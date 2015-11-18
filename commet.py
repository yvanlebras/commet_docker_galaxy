#!/usr/bin/env python
import sys, tempfile, subprocess, glob
import os, re, shutil, argparse
import zipfile, tarfile, gzip
from os.path import basename

"""
WARNING :

commet.py needs commet_exe binaries in your $PATH

commet is available after compiling sources :

http://github.com/pierrepeterlongo/commet

or with the package_commet package in the GenOuest toolshed and the main toolshed

NOTE : 

please add the line #!/usr/bin/env python in top of the Commet.py file if you've a bash error.


"""

def __main__():

	# arguments recuperation
        parser = argparse.ArgumentParser()

        parser.add_argument("--set", dest="set", action='append')
        parser.add_argument("-k", dest="kmer")
        parser.add_argument("-t", dest="minsharedkmer")
        parser.add_argument("-l", dest="minlengthread")
        parser.add_argument("-n", dest="maxn")
        parser.add_argument("-e", dest="minshannonindex")
        parser.add_argument("-m", dest="maxreads")

        parser.add_argument("--output_logs")
        parser.add_argument("--output_vectors")
        parser.add_argument("--output_dendro")
        parser.add_argument("--output_matrix")
        parser.add_argument("--output_heatmap1")
        parser.add_argument("--output_heatmap2")
        parser.add_argument("--output_heatmap3")

        options = parser.parse_args()

	# copy R script into the current dir
	shutil.copy(os.environ['RSCRIPTS']+"/heatmap.r", os.getcwd())
        shutil.copy(os.environ['RSCRIPTS']+"/dendro.R", os.getcwd())

        # prepare input file
        commet_file=open('commet_config_file', 'w')
 
        for set in options.set:
            clean_set=set.replace(',', ';').replace('::', ':')
            commet_file.write(clean_set+"\n")                     
        commet_file.close()

	# edit the command line
	cmd_line=[]
	cmd_line.append("/opt/commet-master/Commet.py")
	cmd_line.extend(["commet_config_file","-b",os.environ['BINARIES'],"-k",options.kmer,"-t",options.minsharedkmer,"-l",options.minlengthread,"-e",options.minshannonindex])

	# add options
	if options.maxn:
		cmd_line.extend(["-n",options.maxn,"-m",options.maxreads])

        print "[COMMAND LINE]"+' '.join(cmd_line)

	# execute job
	p=subprocess.Popen(cmd_line,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdoutput,stderror=p.communicate()
        print stdoutput
        print stderror

	# copy .bv files inside a .bv archive
	tmp_output_dir=os.getcwd()+"/output_commet/"
        os.chdir(tmp_output_dir)

	# create zip outputs
        mybvzipfile=zipfile.ZipFile(tmp_output_dir+'bv.zip.temp', 'w')
        mylogzipfile=zipfile.ZipFile(tmp_output_dir+'log.zip.temp', 'w')
        mymatrixzipfile=zipfile.ZipFile(tmp_output_dir+'matrix.zip.temp', 'w')

	# write files into the specific archive
        list_files = glob.glob(tmp_output_dir+'/*')
        for i in list_files:

		if re.search("\.bv$", i):
			mybvzipfile.write(os.path.basename(i))
		if re.search("\.log$", i):
                        mylogzipfile.write(os.path.basename(i))
		if re.search(".csv$", i):
                        mymatrixzipfile.write(os.path.basename(i))

	# close zip files
	mybvzipfile.close()
	mylogzipfile.close()
        mymatrixzipfile.close()

	# return the archives
	shutil.move(tmp_output_dir+'bv.zip.temp', options.output_vectors)
	shutil.move(tmp_output_dir+'log.zip.temp', options.output_logs)
        shutil.move(tmp_output_dir+'matrix.zip.temp', options.output_matrix)

	# outputs
        try:
            shutil.move(tmp_output_dir+'dendrogram_normalized.png', options.output_dendro)
            shutil.move(tmp_output_dir+'heatmap_percentage.png', options.output_heatmap2)
            shutil.move(tmp_output_dir+'heatmap_normalized.png', options.output_heatmap1)
            shutil.move(tmp_output_dir+'heatmap_plain.png', options.output_heatmap3)
        except:
            print "There is a problem with gplots execution"

if __name__ == "__main__": __main__()

