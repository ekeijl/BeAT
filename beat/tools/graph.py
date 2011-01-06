
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import ColorConverter
from matplotlib.figure import Figure

from django.template import loader
from django.http import HttpResponse

import math

def colorMask(v1,v2):
	cc=ColorConverter()
	mask = []
	for i in range(len(v1)):
		if  v1[i] == v2[i]:
			mask.append(cc.to_rgb('black'))
		elif v1[i] < v2[i]:
			mask.append(cc.to_rgb('red'))
		else:
			mask.append(cc.to_rgb('blue'))
	return mask

def makeScatter(values, titles, superTitle, xLabel, yLabel):
	
	numPlots = len(values)
	fig=Figure(facecolor='w', figsize=(7.5,numPlots*7.5))
	for i, v in enumerate(values):
		if len(v[0]) != 0:
			
			plot = i+1
			
			# Make a subplot for the Total Time data of a benchmark set
			ax=fig.add_subplot(numPlots,1,plot)
					
			t1 = v[0]
			t2 = v[1]
			
			# Color mask: if t[1] < t[2] --> red dot in graph; else blue dot
			t_mask = colorMask(t1,t2)
			
			# Draw a linear function from 1 until the first power of 10 greater than max_value
			max_value_t = max(max(t1),max(t2))
			max_value_t = math.pow(10,math.ceil(math.log10(max_value_t)))
			ax.plot([1,max_value_t], [1,max_value_t],'k-')
			
			# Plot data
			ax.scatter(t1, t2, s=10, color=t_mask, marker='o')
			
			# Axes mark-up
			ax.set_xscale('log')
			ax.set_yscale('log')
			
			if superTitle:
				fig.suptitle(superTitle)
			ax.set_xlabel(xLabel, color='red')
			ax.set_ylabel(yLabel, color='blue')
			
			ax.set_title(titles[i], size='small')
			ax.grid(True)
		
		# Result set is empty
		else: 
			fig.suptitle('Empty result set.')
			fig.set_size_inches(7.5,0.5)
	
	return fig

def export(canvas, title, format='png'):
	"""
	This function exports a matplotlib graph to a given format. Expects a FigureCanvasAgg object (a canvas) to print as a figure.
	Returns a HttpResponse with of the specified mimetype.
	@param canvas The FigureCanvasAgg object.
	@param format The prefered export format. Choose from (png,pdf,ps,eps,svg).
	@param title The title of the exported document.
	"""
	# Set the mimetype of the HttpResponse
	mimetype = ''
	if (format is 'png'):
		mimetype = 'image/png'
	elif (format is 'pdf'):
		mimetype = 'application/pdf'
	elif (format is ('ps' or 'eps')):
		mimetype = 'application/postscript'
	elif (format is 'svg'):
		mimetype = 'image/svg+xml'
	response = HttpResponse(content_type=mimetype)
	
	# Show the user a 'Save as..' dialogue if the graph is not PNG.
	if (format is not 'png'):
		response['Content-Disposition'] = 'attachment; filename=%s.%s' % (title, format)
	# Print to canvas with the right format
	canvas.print_figure(filename=response, format=format, dpi=80)
	return response