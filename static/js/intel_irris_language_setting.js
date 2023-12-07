import {load_html_texts_for_current_language, webui_texts} from './util_load_LanguageSettings_html_texts.js';

document.getElementById('submit_selected_language').addEventListener('submit', make_SetLanguage_HttpPOSTRequest);

const language_HttpRequest_url = '/html_language_configurations'

var supported_iiwa_html_languages = []
var thisPage_webui_texts = {}; // stores the page texts
const thisPage_webui_texts_list = 'intel_irris_language_setting_page';

const iiwa_headers = {
	'Content-Type': 'application/json'
};

/* ****  Function(s) for Web UI language setting **** */
export function load_other_page_text_contents(){
	thisPage_webui_texts = webui_texts;
	//console.log(thisPage_webui_texts)

	document.getElementById('please_select_a_language').innerHTML = thisPage_webui_texts[thisPage_webui_texts_list]['please_select_a_language'];
	document.getElementById('save').innerHTML = thisPage_webui_texts[thisPage_webui_texts_list]['save'];

	get_Supported_IIWA_HTML_Languages();
}

window.addEventListener('onload', load_html_texts_for_current_language("intel_irris_language_setting_page"));
/* ***************************** */

// functions that gets the supported languages in the 'intel_irris_html_language_configurations.json  file 
async function get_Supported_IIWA_HTML_Languages() {
	const response = await fetch(language_HttpRequest_url);
	//console.log(response);
	var received_supported_iiwa_html_languages = await response.json();

	length = Object.keys(received_supported_iiwa_html_languages).length;

	//console.log("Number of supported Web UI languages =  " + length);

	// push language names to list
	for (var i = 0; i < length; i++) {
        supported_iiwa_html_languages = Object.keys(received_supported_iiwa_html_languages['supported_iiwa_html_languages']);
	}
	console.log("Supported Web UI languages : " + supported_iiwa_html_languages);
	update_languageNameSelect();
}

function update_languageNameSelect() {
	var select = document.getElementById("languageName_select");
	select.innerHTML = "";
	var option_language_text = '';

	const select_first_option = thisPage_webui_texts[thisPage_webui_texts_list]['select_a_language'];
	select.options[select.options.length] = new Option(select_first_option);
	for (var x = 0; x < supported_iiwa_html_languages.length; x++) {
		
		// update the select language
		switch (supported_iiwa_html_languages[x]){
			case 'arabic':
				option_language_text = thisPage_webui_texts[thisPage_webui_texts_list]['arabic'];
				break;
			case 'english':
				option_language_text = thisPage_webui_texts[thisPage_webui_texts_list]['english'];
				break;
			default:
				break;
		}

		//option text								//option value
		select.options[select.options.length] = new Option(option_language_text, supported_iiwa_html_languages[x]);
		
		option_language_text = ''; // reset variable
	}
}

// function that submits data from selecting a language form
async function make_SetLanguage_HttpPOSTRequest() {
	var selected_language = document.getElementsByName('languageName_select')[0].value;

	try {
		const RequestResponse = await fetch(language_HttpRequest_url + '/' + selected_language, {
			method: "POST",
			headers: iiwa_headers
		});
		const ResponseContent = await RequestResponse.json();
		return ResponseContent;
	}
	catch (err) {
		console.error(`Error at make_SetLanguage_HttpPOSTRequest : ${err}`);
		throw err;
	}
}



/*
// periodically call the get requests to automatically load new data on the page
var dropdowns_updated = false
function update_Language_Setting_data() {
	if (dropdowns_updated != true) {
		get_Supported_IIWA_HTML_Languages();
	}
	// prevent refreshing dropdowns when an option is selected
	dropdowns_updated = true
	setTimeout(update_Language_Setting_data, 10);
}
update_Language_Setting_data();
*/