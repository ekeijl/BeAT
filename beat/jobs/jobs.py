import sys
import time
import os
import django
from django.template import Template, Context, loader

class Job:
	
	def __init__(self, fileName, script):
		self.name = fileName
		self.script = script


class JobGenerator:
	
	__directory = "."
	jobs = []
	
	def pbsgen(self, nodes, toolname, tooloptions, modelname, prefix="", postfix="", filename=""):
		if not filename:
			filename = toolname
		#t = Template( open(templatepath).read() )
		t = loader.get_template('jTemplate.tpl')
		c = Context({"nodes": nodes, "toolname": toolname, "tooloptions": tooloptions, "modelname":modelname, "prefix":prefix, "postfix":postfix, "filename":filename})
		result = t.render(c);
		return result
	
	def jobgen(self, nodes, toolname, tooloptions, modelname, prefix="", postfix="", filename=None):
		j= Job( filename+".pbs", self.pbsgen(nodes, toolname, tooloptions, modelname, prefix=prefix, postfix=postfix, filename=filename) )
		self.jobs.append(j)
		return j
	
	__ext2type = dict({'.lps': 'lps', '.tbf': 'lpo', '.b': 'nips', '.dve': 'dve', '.etf': 'etf'})
	
	def __extension_to_type(self, extension):
		return self.__ext2type.get(extension)
	
	def suitegen(self, modelname):
		
		base = modelname[:modelname.rfind('.')]
		lang = self.__extension_to_type(modelname[modelname.rfind('.'):])
		
		greytool = lang+"2lts-grey"
		reachtool = lang+"-reach"
		mpitool = lang+"2lts-mpi"
		stdNodes = "1:E5335,walltime=4:00:00"
		filenameBase = base + "-" + lang
		
		self.jobgen( stdNodes, greytool, "", modelname, filename=filenameBase+"-idx" )
		self.jobgen( stdNodes, greytool, "--cache", modelname, filename=filenameBase+"-idx-cache" )
		for vset in ["list", "tree", "fdd"]:
			self.jobgen( stdNodes, greytool, "--state vset --vset "+vset, modelname, filename=filenameBase+"-"+vset )
			self.jobgen( stdNodes, greytool, "--state vset --vset "+vset+" --cache", modelname, filename=filenameBase+"-"+vset+"-cache" )
		for order in ["bfs", "bfs2", "chain"]:
			for vset in ["list", "fdd"]:
				self.jobgen( stdNodes, reachtool, "--order "+order+" --vset "+vset, modelname, filename=filenameBase+"-"+order+"-"+vset )
		
		for W in [1, 2, 4]:
			mpiNodes = str(W)+":ppn=6:E5335,walltime=4:00:00"
			self.jobgen( mpiNodes, mpitool, "", modelname, filename=filenameBase+"-mpi-"+str(W)+"-6", prefix="mpirun -mca btl tcp,self" )
			self.jobgen( mpiNodes, mpitool, "--cache", modelname, filename=filenameBase+"-mpi-cache-"+str(W)+"-6", prefix="mpirun -mca btl tcp,self" )
		
	def generate_all(self):
		contents = os.listdir('.')
		for f in contents:
			if os.path.isfile(f) and os.path.splitext(f)[1] in self.__ext2type:
				self.suitegen(os.path.basename(f))
		

if __name__ == '__main__':
	j = JobGenerator()
	j.generate_all()
	for job in j.jobs:
		print job.name
		if len(sys.argv) > 1:
			with open('./'+job.name, 'w') as f:
				f.write(job.script)
	sys.exit(0)
