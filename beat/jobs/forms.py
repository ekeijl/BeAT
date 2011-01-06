from django import forms
from django.forms import widgets
from beat.benchmarks.models import Benchmark, Model, Algorithm, Tool, OptionValue, AlgorithmTool
from beat.jobs.models import *
from django.shortcuts import get_object_or_404

def ltsminversions():
	#versions = [(v,v) for v in list(set(AlgorithmTool.objects.order_by('version').values_list('version', flat=True).distinct()))]
	return [(v,v) for v in AlgorithmTool.objects.values_list('version',flat=True).distinct().order_by('version')]

class JobGenForm(forms.Form):
	name		= forms.CharField(max_length=255, required=False)
	nodes		= forms.CharField(max_length=255, required=True, initial="1:E5520,walltime=4:00:00")
	tool		= forms.ModelChoiceField(Tool.objects.order_by('name'), empty_label=None, required=True)
	algorithm	= forms.ModelChoiceField(Algorithm.objects.order_by('name'), empty_label=None, required=True)
	options		= forms.CharField(max_length=255, required=False)
	model		= forms.ModelChoiceField(Model.objects.order_by('name'), required=True)
	gitversion	= forms.ChoiceField( choices=ltsminversions() )
	#prefix		= forms.CharField(max_length=255, required=False)
	#postfix		= forms.CharField(max_length=255, required=False)
	
class SuiteGenForm(forms.Form):
	versions	= forms.MultipleChoiceField( choices=ltsminversions(), required=True )
	models		= forms.ModelMultipleChoiceField(Model.objects.order_by('name'), required=True)
