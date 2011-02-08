var testing = false;

function testregex(regex, log){
	if (testing) return;
	testing = true;
	
	var data = {regex: regex, testlog: log};
	$.ajax({
		url: '/regextester/',
		type: 'POST',
		data: data,
		beforeSend: function(){
						$("#ajaxLoad").append('<img src="/site_media/img/ajaxload.gif" />');
					},
		success: function(json){
					handleResponse(json);
				},
		error: function(XMLHttpRequest,textStatus,errorThrown){
					alert("Error with getting testresult: "+textStatus);
				},
		complete: function(){
					testing = false;
					$("#ajaxLoad").html('');
				},
		dataType: 'json'
	});
}

function handleResponse(json){
	$("#id_log_check").val(json.result);
}

$(document).ready(function(){
	$("#testregex").click(function(){
		testregex($("#id_expression").val(),$("#id_test_log").val());
	});
});