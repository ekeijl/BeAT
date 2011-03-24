from beat.benchmarks.models import *
from beat.comparisons.models import *
from django.contrib import admin
from django import forms

class HardwareInline(admin.TabularInline):
	model = BenchmarkHardware
	extra = 1

class OptionValueInline(admin.TabularInline):
	model = BenchmarkOptionValue
	extra = 1

class AlgorithmToolInline(admin.TabularInline):
	model = AlgorithmTool
	extra = 1

class RegexAdmin(admin.ModelAdmin):
	search_fields = ['regex']
	list_display = ('pk', 'regex')

class BenchmarkAdmin(admin.ModelAdmin):
	list_display = ('model', 'algorithm_tool', 'date_time', 'finished', 'user_time', 'system_time', 'total_time', 'elapsed_time', 'memory_VSIZE', 'memory_RSS', 'states_count', 'transition_count')
	list_filter = ['date_time']
	search_fields = ['model__name', 'algorithm_tool__tool__name', 'algorithm_tool__algorithm__name']
	fieldsets = [
		('Configuration', {'fields': ['model','algorithm_tool','finished']}),
		('Date information', {'fields': ['date_time']}),
		('Output data', {'fields': ['user_time', 'system_time','total_time', 'elapsed_time','transition_count','states_count','memory_VSIZE', 'memory_RSS', 'logfile']}),
	]
	inlines = [HardwareInline, OptionValueInline]

class ValidOptionAdmin(admin.ModelAdmin):
	list_display = ('tool', 'algorithm', 'version', 'option')
	search_fields = ['algorithm_tool__algorithm__name', 'algorithm_tool__tool__name', 'algorithm_tool__version', 'option__name']

class ValidOptionInline(admin.TabularInline):
	model = ValidOption
	extra = 1

class RegexForm(forms.ModelForm):
	regex = forms.ModelChoiceField(queryset=Regex.objects.order_by('regex'))
	
	class Meta:
		model = Regex

class AlgorithmToolAdmin(admin.ModelAdmin):
	inlines=[
		ValidOptionInline
	]
	form = RegexForm
	
admin.site.register(Model)
#admin.site.register(Tool, ToolAdmin)
admin.site.register(Tool)
#admin.site.register(Tool)
admin.site.register(Regex, RegexAdmin)
admin.site.register(Hardware)
admin.site.register(Option)
admin.site.register(Benchmark, BenchmarkAdmin)
#admin.site.register(Benchmark)
admin.site.register(Comparison)
admin.site.register(ModelComparison)
admin.site.register(Algorithm)
admin.site.register(RegisteredShortcut)
admin.site.register(ExtraValue)
admin.site.register(AlgorithmTool, AlgorithmToolAdmin)

admin.site.register(ValidOption, ValidOptionAdmin)
admin.site.register(OptionValue)
admin.site.register(BenchmarkOptionValue)
