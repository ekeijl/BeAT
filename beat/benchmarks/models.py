from django.db import models
from django.contrib.auth.models import User
from beat.settings import *

class ModelManager(models.Manager):
	def get_by_natural_key(self, name):
		return self.get(name=name)

class Model(models.Model):
	objects = ModelManager()
	name = models.CharField(max_length=200)
	
	def natural_key(self):
		return self.name

	def __unicode__(self):
		return self.name
	

class OptionValue(models.Model):
	option = models.ForeignKey('Option')
	value = models.CharField(max_length=100)

	def __unicode__(self):
		return "%s = %s" % (self.option.name, self.value)

class Option(models.Model):
	name = models.CharField(max_length=50)
	takes_argument = models.BooleanField()
	
	def __unicode__(self):
		return self.name

class Benchmark(models.Model):
	#Idenifying elements
	model = models.ForeignKey('Model')
	algorithm_tool = models.ForeignKey('AlgorithmTool')
	hardware = models.ManyToManyField('Hardware', through="BenchmarkHardware")
	optionvalue = models.ManyToManyField('OptionValue', through="BenchmarkOptionValue")
	date_time = models.DateTimeField(verbose_name="Time started")
	
	#Data
	user_time = models.DecimalField(max_digits=8,decimal_places=2,verbose_name="User time (s)")
	system_time = models.DecimalField(max_digits=8,decimal_places=2,verbose_name="System time (s)")
	total_time = models.DecimalField(max_digits=8,decimal_places=2,verbose_name="User + System time (s)")
	elapsed_time = models.DecimalField(max_digits=8,decimal_places=2,verbose_name="Elapsed time (s)")
	transition_count = models.BigIntegerField(verbose_name="Transitions", blank=True, null=True) #this may be null
	states_count = models.BigIntegerField(verbose_name="States")
	memory_VSIZE = models.IntegerField(verbose_name="Memory VSIZE (KB)") #rounded to kilobytes
	memory_RSS = models.IntegerField(verbose_name="Memory RSS (KB)") #rounded to kilobytes
	finished = models.BooleanField(verbose_name="Run finished")
	logfile = models.FilePathField(path=LOGS_PATH, blank=True, null=True)
	
	def options(self):
		return "; ".join(map(str,self.optionvalue.all()))

	def disk_space(self):
		return "; ".join(map(str,self.hardware.values_list('disk_space',flat=True)))
		
	def memory(self):
		return "; ".join(map(str,self.hardware.values_list('memory',flat=True)))

	def kernelversion(self):
		return "; ".join(self.hardware.values_list('kernelversion',flat=True))
	
	def cpu(self):
		return "; ".join(self.hardware.values_list('cpu',flat=True))

	def computername(self):
		return "; ".join(self.hardware.values_list('computername', flat=True))

	def __unicode__(self):
		return "%s with %s on %s" % (self.model, self.algorithm_tool, self.date_time)
	
	def get_print_data(self):
		return "model = %s\n algorithmtool = %s\n options = %s\n start time = %s\n User time = %s\n System time = %s\n Elapsed time = %s\n transition count = %s\n state count = %s\n memory VSize = %s\n memory RSS = %s\n finished = %s"%(self.model.name, self.algorithm_tool, self.optionvalue.all(),self.date_time, self.user_time, self.system_time, self.elapsed_time, self.transition_count, self.states_count, self.memory_VSIZE, self.memory_RSS, self.finished)
#self.print_message(V_VERBOSE, "Note: Tried to data to database, but essential data already exists, id: %s from file %s, with data %s"%(bench.pk, f, bench.get_print_data()))		

class Hardware(models.Model):
	computername = models.CharField(max_length=200) 
	memory = models.BigIntegerField(verbose_name="memory (KB)")
	cpu = models.CharField(max_length=200, verbose_name="CPU name")
	disk_space = models.BigIntegerField(verbose_name="disk space (KB)")
	kernelversion = models.CharField(max_length=200, verbose_name="Kernel version")

	def __unicode__(self):
		return "%s @ %sKB RAM, %s, %s" % (self.computername, self.memory, self.cpu, self.kernelversion)
	
	class Meta:
		verbose_name_plural = "Hardware"

class BenchmarkHardware(models.Model):
	benchmark = models.ForeignKey('Benchmark')
	hardware = models.ForeignKey('Hardware')
	
	class Meta:
		verbose_name_plural = "Benchmark Hardware"

class BenchmarkOptionValue(models.Model):
	benchmark = models.ForeignKey('Benchmark')
	optionvalue = models.ForeignKey('OptionValue')
	
	def __unicode__(self):
		return "%s - %s" % (self.benchmark, self.optionvalue)
	
	class Meta:
		verbose_name_plural = "Benchmark OptionValue"

class ExtraValue(models.Model):
	benchmark = models.ForeignKey('Benchmark')
	name = models.CharField(max_length=200)
	value = models.CharField(max_length=200)
	
	def __unicode__(self):
		return "%s=%s" % (self.name, self.value)

class Tool(models.Model):	
	name = models.CharField(max_length=200)
	
	def __unicode__(self):
		return "%s" % (self.name)

class ValidOption(models.Model):
	algorithm_tool = models.ForeignKey('AlgorithmTool')
	option = models.ForeignKey('Option')
	regex = models.ForeignKey('Regex')
	
	def algorithm(self):
		return self.algorithm_tool.algorithm

	def tool(self):
		return self.algorithm_tool.tool

	def version(self):
		return self.algorithm_tool.version

	def __unicode__(self):
		return "%s with option %s" % (self.algorithm_tool.tool.name, self.option.name)

class AlgorithmTool(models.Model):
	algorithm = models.ForeignKey('Algorithm')
	tool = models.ForeignKey('Tool')
	regex = models.ForeignKey('Regex')
	version = models.CharField(max_length=60)
	date = models.DateTimeField()
		
	def __unicode__(self):
		return "%s%s-%s" % (self.tool, self.algorithm, self.version)
	
class Algorithm(models.Model):
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name
	
class Regex(models.Model):
	regex = models.TextField()

	def __unicode__(self):
		return self.regex.split(':')[0] #first ten characters; change to something more elegant later

	class Meta:
		verbose_name_plural = "Regexes"

class RegisteredShortcut(models.Model):
	algorithm_tool = models.ForeignKey('AlgorithmTool')
	option = models.ForeignKey('Option')
	shortcut = models.CharField(max_length=2)
	#note: shortcut should be a letter or a letter followed by a colon
	def __unicode__(self):
		return "%s -> %s in %s" %(self.shortcut,self.option.name, self.algorithm_tool)

