from aqt import mw
from aqt.utils import showInfo
from anki.hooks import addHook
import anki
import os, shutil

MODEL_NAME = 'KaTeX and Markdown'
CONF_NAME = 'MDKATEX'

def create_model_if_necessacy():
    model = mw.col.models.byName(MODEL_NAME + " Basic")
    model_cloze = mw.col.models.byName(MODEL_NAME + " Cloze")
    m = mw.col.models

    if not model:
        create_model()
    if not model_cloze:
        create_model_cloze()
        
    update()


def create_model():
    m = mw.col.models
    model = m.new(MODEL_NAME + " Basic")

    field = m.newField("Front")
    m.addField(model, field)

    field = m.newField("Back")
    m.addField(model, field)

    template = m.newTemplate(MODEL_NAME + " Basic")
    template['qfmt'] = front
    template['afmt'] = back
    model['css'] = css

    m.addTemplate(model, template)
    m.add(model)
    m.save(model)


def create_model_cloze():
    m = mw.col.models
    model = m.new(MODEL_NAME + " Cloze")
    model["type"] = anki.consts.MODEL_CLOZE

    field = m.newField("Text")
    m.addField(model, field)

    field = m.newField("Back Extra")
    m.addField(model, field)

    template = m.newTemplate(MODEL_NAME + " Cloze")
    template['qfmt'] = front_cloze
    template['afmt'] = back_cloze
    model['css'] = css

    m.addTemplate(model, template)
    m.add(model)
    m.save(model)
    
def update():
    model = mw.col.models.byName(MODEL_NAME + " Basic")
    model_cloze = mw.col.models.byName(MODEL_NAME + " Cloze")

    model['tmpls'][0]['qfmt'] = front
    model['tmpls'][0]['afmt'] = back
    model['tmpls'][0]['css'] = css

    model_cloze['tmpls'][0]['qfmt'] = front_cloze
    model_cloze['tmpls'][0]['afmt'] = back_cloze
    model_cloze['tmpls'][0]['css'] = css

    mw.col.models.save(model)
    mw.col.models.save(model_cloze)

    if os.path.isdir(os.path.join(mw.col.media.dir(), "_katex")):
        shutil.rmtree(os.path.join(mw.col.media.dir(), "_katex"))

    if os.path.isdir(os.path.join(mw.col.media.dir(), "_markdown-it")):
        shutil.rmtree(os.path.join(mw.col.media.dir(), "_markdown-it"))

    addon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        
    _add_file(os.path.join(addon_path, "_katex.min.js"), "_katex.min.js")
    _add_file(os.path.join(addon_path, "_katex.css"), "_katex.css")
    _add_file(os.path.join(addon_path, "_auto-render.js"), "_auto-render.js")
    _add_file(os.path.join(addon_path, "_markdown-it.min.js"), "_markdown-it.min.js")

    for katex_font in os.listdir(os.path.join(addon_path, "fonts")):
        _add_file(os.path.join(addon_path, "fonts", katex_font), katex_font)

def _add_file(path, filename):
    if not os.path.isfile(os.path.join(mw.col.media.dir(), filename)):
        mw.col.media.add_file(path)

addHook("profileLoaded", create_model_if_necessacy)

front = """
<div id="front"><pre>{{Front}}</pre></div>

<script>
	var getResources = [
		getCSS("_katex.css", "this.href='https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.css"),
		getScript("_katex.min.js", "https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.js"),
		getScript("_auto-render.js", "https://cdn.jsdelivr.net/gh/Jwrede/Anki-KaTeX-Markdown/auto-render-cdn.js"),
		getScript("_markdown-it.min.js", "https://cdnjs.cloudflare.com/ajax/libs/markdown-it/12.0.4/markdown-it.min.js")
	];

	Promise.all(getResources).then(render).catch(show);
	

	function getScript(path, altURL) {
		return new Promise((resolve, reject) => {
			let script = document.createElement("script");
			script.onload = resolve;
			script.onerror = function() {
				let script_online = document.createElement("script");
				script_online.onload = resolve;
				script_online.onerror = reject;
				script_online.src = altURL;
				document.head.appendChild(script_online);
			}
			script.src = path;
			document.head.appendChild(script);
		})
	}

	function getCSS(path, altURL) {
		return new Promise((resolve, reject) => {
			var css = document.createElement('link');
			css.setAttribute('rel', 'stylesheet');
			css.type = 'text/css';
			css.onload = resolve;
			css.onerror = function() {
				var css_online = document.createElement('link');
				css_online.setAttribute('rel', 'stylesheet');
				css_online.type = 'text/css';
				css_online.onload = resolve;
				css.onerror = reject;
				css.href = altURL;
				document.head.appendChild(css);
			}
			css.href = path;
			document.head.appendChild(css);
		});
	}


	function render() {
		renderMath("front");
		markdown("front");
		show();
	}

	function show() {
		document.getElementById("front").style.visibility = "visible ";
	}

	function renderMath(ID) {
		let text = document.getElementById(ID).innerHTML;
		text = replaceInString(text);
		text = decodeHtml(text);
		console.log(text);
		document.getElementById(ID).innerHTML = text;
		renderMathInElement(document.getElementById(ID), {
			delimiters:  [
  				{left: "$$", right: "$$", display: true},
  				{left: "$", right: "$", display: false}
			],
		});
	}

	function decodeHtml(html) {
   		var txt = document.createElement("textarea");
    	txt.innerHTML = html;
    	return txt.value;
	}

	function markdown(ID) {
		let md = new markdownit({typographer: true, html:true});
		let text = document.getElementById(ID).innerHTML;
		text = decodeHtml(text);
		document.getElementById(ID).innerHTML = md.render(text);
	}
	function replaceInString(str) {
		str = str.replace(/<[\/]?pre>/gi, "");
		str = str.replace(/<br\s*[\/]?>/gi, "\\n");
		str = str.replace(/<div>/g, "\\n");
		// Thanks Graham A!
		str = str.replace(/<[\/]?span[^>]*>/gi, "")
		return str.replace(/<\/div>/g, "\\n");
	}
</script>
"""

back = """

<div id="front"><pre>{{Front}}</pre></div>

<hr id=answer>

<div id="back"><pre>{{Back}}</pre></div>

<script>
	var getResources = [
		getCSS("_katex.css", "this.href='https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.css"),
		getScript("_katex.min.js", "https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.js"),
		getScript("_auto-render.js", "https://cdn.jsdelivr.net/gh/Jwrede/Anki-KaTeX-Markdown/auto-render-cdn.js"),
		getScript("_markdown-it.min.js", "https://cdnjs.cloudflare.com/ajax/libs/markdown-it/12.0.4/markdown-it.min.js")
	];

	Promise.all(getResources).then(render).catch(show);
	

	function getScript(path, altURL) {
		return new Promise((resolve, reject) => {
			let script = document.createElement("script");
			script.onload = resolve;
			script.onerror = function() {
				let script_online = document.createElement("script");
				script_online.onload = resolve;
				script_online.onerror = reject;
				script_online.src = altURL;
				document.head.appendChild(script_online);
			}
			script.src = path;
			document.head.appendChild(script);
		})
	}

	function getCSS(path, altURL) {
		return new Promise((resolve, reject) => {
			var css = document.createElement('link');
			css.setAttribute('rel', 'stylesheet');
			css.type = 'text/css';
			css.onload = resolve;
			css.onerror = function() {
				var css_online = document.createElement('link');
				css_online.setAttribute('rel', 'stylesheet');
				css_online.type = 'text/css';
				css_online.onload = resolve;
				css.onerror = reject;
				css.href = altURL;
				document.head.appendChild(css);
			}
			css.href = path;
			document.head.appendChild(css);
		});
	}

	function render() {
		renderMath("front");
		markdown("front");
		renderMath("back");
		markdown("back");
		show();
	}

	function show() {
		document.getElementById("front").style.visibility = "visible ";
		document.getElementById("back").style.visibility = "visible ";
	}


	function renderMath(ID) {
		let text = document.getElementById(ID).innerHTML;
		text = replaceInString(text);
		text = decodeHtml(text);
		document.getElementById(ID).innerHTML = text;
		renderMathInElement(document.getElementById(ID), {
			delimiters:  [
  				{left: "$$", right: "$$", display: true},
  				{left: "$", right: "$", display: false}
			],
		});
	}
	function decodeHtml(html) {
   		var txt = document.createElement("textarea");
    	txt.innerHTML = html;
    	return txt.value;
	}
	function markdown(ID) {
		let md = new markdownit({typographer: true, html:true});
		let text = document.getElementById(ID).innerHTML;
		text = decodeHtml(text);
		document.getElementById(ID).innerHTML = md.render(text);
	}
	function replaceInString(str) {
		str = str.replace(/<[\/]?pre>/gi, "");
		str = str.replace(/<br\s*[\/]?>/gi, "\\n");
		str = str.replace(/<div>/g, "\\n");
		// Thanks Graham A!
		str = str.replace(/<[\/]?span[^>]*>/gi, "")
		return str.replace(/<\/div>/g, "\\n");
	}
</script>


"""

front_cloze = """

<div id="front"><pre>{{cloze:Text}}</pre></div>

<script>
	var getResources = [
		getCSS("_katex.css", "this.href='https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.css"),
		getScript("_katex.min.js", "https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.js"),
		getScript("_auto-render.js", "https://cdn.jsdelivr.net/gh/Jwrede/Anki-KaTeX-Markdown/auto-render-cdn.js"),
		getScript("_markdown-it.min.js", "https://cdnjs.cloudflare.com/ajax/libs/markdown-it/12.0.4/markdown-it.min.js")
	];

	Promise.all(getResources).then(render).catch(show);
	

	function getScript(path, altURL) {
		return new Promise((resolve, reject) => {
			let script = document.createElement("script");
			script.onload = resolve;
			script.onerror = function() {
				let script_online = document.createElement("script");
				script_online.onload = resolve;
				script_online.onerror = reject;
				script_online.src = altURL;
				document.head.appendChild(script_online);
			}
			script.src = path;
			document.head.appendChild(script);
		})
	}

	function getCSS(path, altURL) {
		return new Promise((resolve, reject) => {
			var css = document.createElement('link');
			css.setAttribute('rel', 'stylesheet');
			css.type = 'text/css';
			css.onload = resolve;
			css.onerror = function() {
				var css_online = document.createElement('link');
				css_online.setAttribute('rel', 'stylesheet');
				css_online.type = 'text/css';
				css_online.onload = resolve;
				css.onerror = reject;
				css.href = altURL;
				document.head.appendChild(css);
			}
			css.href = path;
			document.head.appendChild(css);
		});
	}
	function render() {
		renderMath("front");
		markdown("front");
		show();
	}
	function show() {
		document.getElementById("front").style.visibility = "visible ";
	}
	function renderMath(ID) {
		let text = document.getElementById(ID).innerHTML;
		text = replaceInString(text);
		text = decodeHtml(text);
		document.getElementById(ID).innerHTML = text;
		renderMathInElement(document.getElementById(ID), {
			delimiters:  [
  				{left: "$$", right: "$$", display: true},
  				{left: "$", right: "$", display: false}
			],
		});
	}
	function markdown(ID) {
		let md = new markdownit({typographer: true, html:true});
		let text = document.getElementById(ID).innerHTML;
		text = decodeHtml(text);
		document.getElementById(ID).innerHTML = md.render(text);
	}
	function decodeHtml(html) {
   		var txt = document.createElement("textarea");
    	txt.innerHTML = html;
    	return txt.value;
	}
	function replaceInString(str) {
		str = str.replace(/<[\/]?pre>/gi, "");
		str = str.replace(/<br\s*[\/]?>/gi, "\\n");
		str = str.replace(/<div>/g, "\\n");
		// Thanks Graham A!
		str = str.replace(/<[\/]?span[^>]*>/gi, "")
		return str.replace(/<\/div>/g, "\\n");
	}
</script>
"""

back_cloze = """
<div id="back"><pre>{{cloze:Text}}</pre></div><br>
<div id="extra"><pre>{{Back Extra}}</pre></div>

<script>
	var getResources = [
		getCSS("_katex.css", "this.href='https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.css"),
		getScript("_katex.min.js", "https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.js"),
		getScript("_auto-render.js", "https://cdn.jsdelivr.net/gh/Jwrede/Anki-KaTeX-Markdown/auto-render-cdn.js"),
		getScript("_markdown-it.min.js", "https://cdnjs.cloudflare.com/ajax/libs/markdown-it/12.0.4/markdown-it.min.js")
	];

	Promise.all(getResources).then(render).catch(show);
	

	function getScript(path, altURL) {
		return new Promise((resolve, reject) => {
			let script = document.createElement("script");
			script.onload = resolve;
			script.onerror = function() {
				let script_online = document.createElement("script");
				script_online.onload = resolve;
				script_online.onerror = reject;
				script_online.src = altURL;
				document.head.appendChild(script_online);
			}
			script.src = path;
			document.head.appendChild(script);
		})
	}

	function getCSS(path, altURL) {
		return new Promise((resolve, reject) => {
			var css = document.createElement('link');
			css.setAttribute('rel', 'stylesheet');
			css.type = 'text/css';
			css.onload = resolve;
			css.onerror = function() {
				var css_online = document.createElement('link');
				css_online.setAttribute('rel', 'stylesheet');
				css_online.type = 'text/css';
				css_online.onload = resolve;
				css.onerror = reject;
				css.href = altURL;
				document.head.appendChild(css);
			}
			css.href = path;
			document.head.appendChild(css);
		});
	}


	function render() {
		renderMath("back");
		markdown("back");
		renderMath("extra");
		markdown("extra");	
		show();
	}

	function show() {
		document.getElementById("back").style.visibility = "visible ";
		document.getElementById("extra").style.visibility = "visible ";
	}

	function renderMath(ID) {
		let text = document.getElementById(ID).innerHTML;
		text = replaceInString(text);
		text = decodeHtml(text);
		document.getElementById(ID).innerHTML = text;
		renderMathInElement(document.getElementById(ID), {
			delimiters:  [
  				{left: "$$", right: "$$", display: true},
  				{left: "$", right: "$", display: false}
			],
		});
	}
	function markdown(ID) {
		let md = new markdownit({typographer: true, html:true});
		let text = document.getElementById(ID).innerHTML;
		text = decodeHtml(text);
		document.getElementById(ID).innerHTML = md.render(text);
	}
	function decodeHtml(html) {
   		var txt = document.createElement("textarea");
    	txt.innerHTML = html;
    	return txt.value;
	}
	function replaceInString(str) {
		str = str.replace(/<[\/]?pre>/gi, "");
		str = str.replace(/<br\s*[\/]?>/gi, "\\n");
		str = str.replace(/<div>/g, "\\n");
		// Thanks Graham A!
		str = str.replace(/<[\/]?span[^>]*>/gi, "")
		return str.replace(/<\/div>/g, "\\n");
	}
</script>
"""

css = """
.card {
  font-family: arial;
  font-size: 20px;
  color: black;
  background-color: white;
}
table, th, td {
	border: 1px solid black;
	border-collapse: collapse;
}
#front, #back, #extra {
	visibility: hidden;
}
"""
