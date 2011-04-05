import csv
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext, loader
from django.db.models.loading import get_model

def export(qs, title="QuerySet", exclude=[], include=[]):
	model = qs.model
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=%s.csv' % title
	writer = csv.writer(response)
	# Write headers to CSV file
	headers = []
	
	if (include):
		for field in include:
			f = field.split('__')
			if len(f) != 1:
				headers.append((f[0],f[1]))
			else:
				headers.append((f[0],""))
	else:
		for field in model._meta.fields:
			if not (field.name in exclude):
				headers.append((field.name, ""))
	writer.writerow([a+"__"+b if b != "" else a for (a,b) in headers])
	# Write data to CSV file
	for obj in qs:
		row = []
		for (a,b) in headers:
			val = getattr(obj, a)
			if b != "":
				val = getattr(val,b)
			
			if callable(val):
				val = val()
			row.append(val)
		writer.writerow(row)
	# Return CSV file to browser as download
	return response
