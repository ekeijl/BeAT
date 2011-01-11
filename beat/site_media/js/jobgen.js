var testing = false;

function test(job){
	if (testing) return;
	testing = true;
	
	var data = {job: job};
	$.ajax({
		url: '/ajax_jobgen/',
		type: 'POST',
		data: data,
		beforeSend: function(){
						$("#ajaxLoad").append('<img src="/site_media/img/ajaxload.gif" />');
					},
		success: function(json){
					$("#id_name").val(json.name);
					$("#id_nodes").val(json.nodes);
					$("#id_tool").val(json.tool);
					$("#id_algorithm").val(json.algorithm);
					$("#id_model").val(json.model);
					$("#id_gitversion").val(json.gitversion);
					$("#id_options").val(json.options);
				},
		error: function(XMLHttpRequest,textStatus,errorThrown){
					alert("Error with getting result: "+textStatus);
				},
		complete: function(){
					testing = false;
					$("#ajaxLoad").html('');
				},
		dataType: 'json'
	});
}

$(document).ready(function(){
	$("#id_list").change(function(){
		var job = $("#id_list option:selected").val();
		if (job == "") {
			$("#id_name").val('');
			$("#id_nodes").val('');
			$("#id_model").val('');
			$("#id_options").val('');
		} else {
			test(job);
		}
	});
});