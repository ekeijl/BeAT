var testing = false;

function test(at){
	if (testing) return;
	testing = true;
	
	var data = {at: at};
	$.ajax({
		url: '/ajax_tool_upload/',
		type: 'POST',
		data: data,
		beforeSend: function(){
						$("#ajaxLoad").append('<img src="/site_media/img/ajaxload.gif" />');
					},
		success: function(json){
					$("#id_version_name").val(json.version);
					$("#id_tool_name").val(json.tool);
					$("#id_expression").val(json.regex);
					$("#id_algorithm_name").val(json.algorithm);
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
	$("#id_at").change(function(){
		var at = $("#id_at option:selected").val();
		if (at == "") {
			$("#id_version_name").val('');
			$("#id_tool_name").val('');
			$("#id_expression").val('');
			$("#id_algorithm_name").val('');
			
		} else {
			test(at);
		}
	});
});