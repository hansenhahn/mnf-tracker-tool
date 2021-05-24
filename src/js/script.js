
const API_URL = "http://127.0.0.1:5000";

let apiFunc = "";
let jsonData = [];
let jsonDataFiltered = [];

let queryFilter = "";

const TIMER_REFRESH_RATE = 60;

let timerCount = 0;
var timerLoop = null;

/* */
function pageRefreshNow()
{
	if ( $("#input-filter").length != 0 )
	{
		queryFilter = $("#input-filter").val();
	}
	else
	{
		queryFilter = "";
	}
	
	timerCount = 0;
	timerUpdateLoop();
	return false;
}

/* */
function timerUpdateLoop()
{	 
	if ( timerLoop == null )
		timerLoop = setInterval(timerUpdateLoop, 1000);

	if ( timerCount == 0 )
	{
		timerCount = TIMER_REFRESH_RATE;
		$.getJSON(API_URL + apiFunc, function(data){
			jsonData = data;
			if ( queryFilter != "" ){
				queryFilter = queryFilter.toLowerCase();
				jsonDataFiltered = jsonData.filter(e => ((e.serialNumber == queryFilter) ||
														(e.iop.toLowerCase().includes(queryFilter)) ||
														(e.client.toLowerCase().includes(queryFilter))) );
			}
			else{ 
				jsonDataFiltered = jsonData;
			}				
			pageCallback(jsonDataFiltered);
		});
	}
	
	var hour = ('00' + Math.floor(timerCount / (60*60))).slice(-2);
	var min = ('00' + Math.floor(timerCount / 60)).slice(-2);
	var sec = ('00'+ Math.floor(timerCount % 60)).slice(-2);
	$("#update-timer").html(hour + ":" + min + ":" + sec + "   <span class=\"glyphicon glyphicon-refresh\"/>");
	timerCount--;
}

const PAGE_RENDERMODE_LOG_TABLE = 0;
const PAGE_RENDERMODE_GROUP_TABLE = 1;

const PAGE_FOOTER_STEP = 10;
const PAGE_ROW_STEP = 50;

var pageCallback = null;

let pageIndexRoot = 0;
let pageSelected = 0;

function pageSetCallbackFunc(mode)
{
	switch (mode)
	{
		case PAGE_RENDERMODE_LOG_TABLE:
			pageCallback = pageRenderLogTable;
			apiFunc = "/api/v1/track";
			break;
		case PAGE_RENDERMODE_GROUP_TABLE:
			pageCallback = pageRenderGroupTable;
			apiFunc = "/api/v1/track/last";
			break;
	}
}

function pageRenderLogTable(obj)
{	
	$("#update-modal").show();

	var content = "";
	
	for(var i = 0; i < PAGE_ROW_STEP ; i++)
	{
		if ( ((pageSelected*PAGE_ROW_STEP)+i) === obj.length )
		{
			break;
		}		
		
		var t = new Date(obj[((pageSelected*PAGE_ROW_STEP)+i)].timestamp*1000);

		content += "<tr>" + 
						"<th>" + t.toLocaleDateString("pt-BR") + " " + t.toLocaleTimeString("pt-BR") + "</th>" +
						"<th>" + obj[((pageSelected*PAGE_ROW_STEP)+i)].iop + "</th>" +
						"<th>" + obj[((pageSelected*PAGE_ROW_STEP)+i)].serialNumber + "</th>" +
						"<th>" + obj[((pageSelected*PAGE_ROW_STEP)+i)].equipment + "</th>" +
						"<th>" + obj[((pageSelected*PAGE_ROW_STEP)+i)].step + "</th>" +
						"<th>" + obj[((pageSelected*PAGE_ROW_STEP)+i)].client + "</th>" +
					"</tr>";
	}
	
	$(".table tbody").html(content);
	
	pageIndexesGenerate(Math.ceil(obj.length/PAGE_ROW_STEP));
	
	$("#update-modal").hide();
}

function pageRenderGroupTable(obj)
{
	const STEP = ["MONTAGEM","PRÉ-CALIBRAÇÃO","CALIBRAÇÃO","PRÉ-ESTUFA","ESTUFA","PÓS-ESTUFA","RUNIN","FINALIZAÇÃO","FIM"];
	
	$("#update-modal").show();
	
	var dict = {};
	
	for(var i = 0; i < obj.length ; i++)
	{
		var client = obj[i].iop + ' - ' + obj[i].client;
		
		if (!( client in dict))
		{
			dict[client] = {};
			dict[client]["__total__"] = 0;
			for(var j = 0; j < STEP.length; j++)
				dict[client][STEP[j]] = 0;
		}
		
		if ( obj[i].step in dict[client] )
		{
			dict[client][obj[i].step] += 1;
		}
	
		dict[client]["__total__"] += 1;
	}
	
	
	var content = "";
	for (var key in dict)
	{
		if ( dict[key]["__total__"] === 0 )
			continue;	
	
		if ( dict[key]["__total__"] === dict[key][STEP[STEP.length-1]] )
			content += "<div class=\"row card-equipment card-equipment-done\">";
		else
			content += "<div class=\"row card-equipment\">";
		
		//content += "<div class=\"col-sm-1\"><img src=\"web-content/PQ-700_card_info.14bd7bdd.svg\"></div>";
		content += "<div class=\"col-sm-12\">";
		content += "<div class=\"row text-left\">";
		content += "<div class=\"col-sm-12 bg-dark\" style=\"padding:8px;font-size:18px;\">" + key + "</div>"

		for ( var j = 0 ; j < STEP.length ; j++ )
		{
			content +=	"<div class=\"col-sm-3\" style=\"padding:5px\">" + STEP[j] + ": " + dict[key][STEP[j]] + "</div>";
		}
		
		content += "<div class=\"col-sm-12\" style=\"padding:4px\">" + "Total: " + dict[key]["__total__"] + "</div>";
		content += "</div>";
		content += "</div>";
		content += "</div>";		
	}

	$("#update-pi").html(content);
	
	$("#update-modal").hide();
}

function pageIndexesGenerate(pageSize)
{	
	var content = "";
	
	if ( pageIndexRoot > 0 )
	{
		content += "<span class=\"btn-page-index bg-light\" onclick=\"pageIndexesStepBackward()\">&lt</span>\n";
	}
	
	for( var i = 0 ; i < PAGE_FOOTER_STEP ; i++ )
	{
		if ( (pageIndexRoot+i) === pageSize )
			break;
		
		if ( (pageIndexRoot+i) === pageSelected )
		{
			content += "<span class=\"btn-page-index bg-dark\">" + (pageIndexRoot+i+1) + "</span>\n";			
		}
		else 
		{
			content += "<span class=\"btn-page-index bg-light\" onclick=\"pageIndexesSelectPage(" + (pageIndexRoot+i) + ")\">" + (pageIndexRoot+i+1) + "</span>\n";
		}
	}
	
	if ( (pageIndexRoot+i) < pageSize )
	{
		content += "<span class=\"btn-page-index bg-light\" onclick=\"pageIndexesStepForward()\">&gt</span>\n";
	}
	
	$(".btn-page-indexes-group").html(content);
}

function pageIndexesSelectPage(value)
{
	pageSelected = value;
	pageCallback(jsonDataFiltered);
}

function pageIndexesStepForward()
{
	pageIndexRoot += PAGE_FOOTER_STEP;
	pageSelected = pageIndexRoot;
	pageCallback(jsonDataFiltered);
}

function pageIndexesStepBackward()
{
	pageIndexRoot -= PAGE_FOOTER_STEP;
	pageSelected = pageIndexRoot;
	pageCallback(jsonDataFiltered);
}