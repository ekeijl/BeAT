from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_list_or_404
import datetime
from filereader import FileReader
from beat.benchmarks.models import Benchmark, Comparison
from forms import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# MatPlotLib
import numpy as np

# Log upload
from beat.benchmarks.log_upload import handle_uploaded_file

# Log upload
def upload_log(request):
	if request.method == 'POST':
		form = UploadLogForm(request.POST, request.FILES)
		if form.is_valid():
			title = form.cleaned_data['title']
			handle_uploaded_file(request.FILES['file'], title)
			try:
				FileReader.main(FileReader(), [os.path.join(beat.settings.STATIC_MEDIA_ROOT, 'upload', 'logs') + "%s"%(request.FILES['file'])], 2)
			except:
				return HttpResponse('error')
			else:
				return HttpResponse('ok')
	else:
		form = UploadLogForm()
	return render_to_response('upload_log.html', {'form': form}, context_instance=RequestContext(request))

def scatterplot(request):
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.figure import Figure
	import math
	fig=Figure(facecolor='w')
	ax=fig.add_subplot(211)
	
	# ELAPSED TIME
	b1 = Benchmark.objects.filter(tool__name__exact='lpo')
	b2 = Benchmark.objects.filter(tool__name__exact='nips').filter(model__in=[b.model.pk for b in b1])
	b1 = b1.filter(model__in=[b.model.pk for b in b2])
	
	t1 = [b.elapsed_time for b in b1]
	t2 = [b.elapsed_time for b in b2]
	
	# Draw a linear function from .001 until the first power of 10 greater than max_value
	max_value_t = max(max(b1.values('elapsed_time')),max(b2.values('elapsed_time')))['elapsed_time']
	max_value_t = math.pow(10,math.ceil(math.log10(max_value_t)))
	ax.plot(np.arange(0,max_value_t,step=.001),np.arange(0,max_value_t,step=.001),'b-')
	
	# Plot data
	ax.plot(t1, t2, 'ro')
	
	# Axes mark up
	ax.set_xscale('log')
	ax.set_yscale('log')
	ax.set_xlabel('lpo')
	ax.set_ylabel('nips')
	ax.set_title('Runtime (s)', size='small')
	ax.grid(True)
		
	# MEMORY
	ax=fig.add_subplot(212)
	m1 = [b.memory_VSIZE for b in b1]
	m2 = [b.memory_VSIZE for b in b2]
	
	max_value_m = max(max(b1.values('memory_VSIZE')),max(b2.values('memory_VSIZE')))['memory_VSIZE']
	max_value_m = math.pow(10,math.ceil(math.log10(max_value_m)))
	ax.plot(np.arange(0,max_value_m),np.arange(0,max_value_m),'b-')
	
	ax.set_xscale('log')
	ax.set_yscale('log')
	ax.set_xlabel('lpo')
	ax.set_ylabel('nips')
	ax.grid(True)
	
	ax.plot(m1,m2,'ro')
	ax.set_title('Memory VSIZE (kb)', size='small')
	
	fig.set_size_inches(5,10)
	canvas = FigureCanvas(fig)
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response

def simple(request, id):
	
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.figure import Figure
	fig=Figure(facecolor='w')
	ax=fig.add_subplot(211)
	
	# DB stuff
	benchmark_IDs = Comparison.objects.get(pk=id)
	benchmarks = Benchmark.objects.filter(pk__in=benchmark_IDs.benchmarks.split(','))
	states = [b.states_count for b in benchmarks]
	elapsed_time = [b.elapsed_time for b in benchmarks]
	memory_vsize = [b.memory_VSIZE for b in benchmarks]
	
	# Plot data
	width = 0.4
	numBench = benchmarks.count()
	ax.bar(np.arange(numBench), states, width, align='center')
	ax.set_xticks(np.arange(benchmarks.count()))
	ax.set_xticklabels(benchmarks, size='small')
	ax.set_ylabel('States')
	#ax.figure.set_figheight(2)
	ax.grid(True)
	
	# Output
	ax=fig.add_subplot(212)
	ax.plot(elapsed_time, memory_vsize, 'ro')
	ax.set_xlabel('Elapsed Time')
	ax.set_ylabel('Memory VSIZE')
	
	#fig.set_size_inches(4,8)
	canvas = FigureCanvas(fig)
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response

def graph_model(request, models=None, type='states', options=None):
	# General library stuff
	from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
	from matplotlib.lines import Line2D
	from matplotlib.figure import Figure
	
	#DB stuff
	from django.db.models import Count
	from beat.benchmarks.models import Model

	fig=Figure(facecolor='w')
	ax=fig.add_subplot(111)
	
	colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
	styles = ['-', '--', ':']
	markers = ['+','o','x']

	# Plot data
	axisNum = 0
	modelNames = Model.objects.values('name').annotate(num_models=Count('name'))
	for m in modelNames:
		axisNum += 1
		style = styles[axisNum % len(styles) ]
		color = colors[axisNum % len(colors) ]
		marker = markers[axisNum % len(markers) ]
		
		benchmarks = Benchmark.objects.filter(model__name__exact = m['name'])
		if models is not None:
			benchmarks = benchmarks.filter(model__name in models)
		types = {
			'transitions': [b.transition_count for b in benchmarks],
			'states': [b.states_count for b in benchmarks],
			'vsize': [b.memory_VSIZE for b in benchmarks],
			'rss': [b.memory_RSS for b in benchmarks],
		}[type]
		lines = ax.plot(
			[b.model.version for b in benchmarks], 
			types, 
			marker + style + color,
			label = m['name'])

	#Mark-up
	ax.set_title(type + ' vs Version')
	leg = ax.legend()
	for t in leg.get_texts():
		t.set_fontsize('small')
	ax.set_ylabel(type)
	ax.set_xlabel('Version')
	
	# Output
	canvas = FigureCanvas(fig)
	#fig.savefig('benchmark.pdf')
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response

	#@login_required(redirect_field_name='next')
def index(request):
	return render_to_response('base.html', context_instance=RequestContext(request))

@login_required
def benchmarks(request, numResults=25):
	benches = Benchmark.objects.all()
	paginator = Paginator(benches, numResults, orphans=10)
	
	# Make sure page request is an int. If not, deliver first page.
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	# If page request (9999) is out of range, deliver last page of results.
	try:
		benches = paginator.page(page)
	except (EmptyPage, InvalidPage):
		benches = paginator.page(paginator.num_pages)

	return render_to_response('benchmarks.html', { 'benchmarks' : benches }, context_instance=RequestContext(request))

@login_required()
def compare(request):
	if request.method == 'POST': # If the form has been submitted...
		form = CompareForm(request.POST) # A form bound to the POST data
		if (form.is_valid()):
			# Process the data in form.cleaned_data
			b = form.cleaned_data['benchmarks']
			comparison, created = Comparison.objects.get_or_create(user=request.user, benchmarks=(",".join([str(bench.id) for bench in b])))
			return render_to_response('compare.html', { 'id' : comparison.id }, context_instance=RequestContext(request))
	else:
		return redirect(benchmarks.views.benchmarks)

def compare_detail(request, id):
	return render_to_response('compare.html', { 'id' : id }, context_instance=RequestContext(request))
	
@login_required()
def user_comparisons(request):
	c = get_list_or_404(Comparison, user=request.user.id)
	return render_to_response('user_compare.html', { 'comparisons' : c }, context_instance=RequestContext(request))
	
def user_comparison_delete(request, id):
	c = Comparison.objects.get(pk=id)
	c.delete()
	return redirect('/user/compare/')
	
def compare_model(request):
	if request.method == 'POST': # If the form has been submitted...
		form = CompareModelsForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			type = form.cleaned_data['type']
			return render_to_response('compare_models.html', { 'type' : type }, context_instance=RequestContext(request))
	else:
		form = CompareModelsForm() # An unbound form
		
	return render_to_response('compare_models_form.html', {
		'form': form, 
	}, context_instance=RequestContext(request))