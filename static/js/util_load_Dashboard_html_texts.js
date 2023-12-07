import {load_other_dashboard_text_contents} from './intel_irris_dashboard.js';

const html_texts_for_current_language_url = '/html_texts_for_current_language';

export var webui_texts = {}; // stores the texts, in JSON, for the page

let current_language = '';
let for_page = ''; // stores the name of the current page

/* ** Function(s) for Web UI language setting ** */

// puts the html texts in a variable
export async function load_html_texts_for_current_language(passed_page){
    for_page = passed_page;
    console.log("[util] loading HTML texts for the page : " + for_page);
    const response = await fetch(html_texts_for_current_language_url);
    console.log(response);
    webui_texts = await response.json();
    current_language = webui_texts['current_language'];

    //console.log("Web UI texts in current language :");
    //console.log(webui_texts);

    set_title();
    set_text_direction();
    set_menu_names();
    set_h1();

    switch (for_page){
        case 'dashboard_page':
            load_other_dashboard_text_contents();
            break;
        default:
            break;
    }
}

// sets the page title
function set_title(){
    switch (for_page){
        case 'dashboard_page':
            document.title = webui_texts['dashboard_page']['title'];
            break;
        default:
            //console.log("[util] cannot set HTML texts for the page!!")
            break;
    }  
}

// set the text-align style in CSS
function set_text_direction(){
    // style content with right-to-left 
    if (current_language == 'arabic'){
        document.documentElement.style.setProperty('--body_direction', 'rtl');
        // set the card footer images to reverse direction
        document.documentElement.style.setProperty('--card_footer_images_float_left', 'right');
        document.documentElement.style.setProperty('--card_footer_images_float_right', 'left');
    }
}

// sets the menu names
function set_menu_names(){
    // style content on menu_bar.css as rtl or ltr
    if (current_language == 'arabic'){
        document.documentElement.style.setProperty('--responsive_text_align', 'right');
    }
    document.getElementById('menu_dashboard').innerHTML = webui_texts['menu']['dashboard'];
    document.getElementById('menu_device_manager').innerHTML = webui_texts['menu']['device_manager'];
    document.getElementById('menu_language_setting').innerHTML = webui_texts['menu']['language_setting'];
}

// sets h1 text
function set_h1(){
    switch (for_page){
        case 'dashboard_page':
            document.getElementById('h1').innerHTML = webui_texts['dashboard_page']['h1'];
            break;
        default:
            //console.log("[util] cannot set HTML texts for the page!!")
    }
}

/* ***************************** */