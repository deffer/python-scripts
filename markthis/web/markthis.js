sel = null
function updateSel(nsel){
	window.sel = nsel
	content = nsel.extractContents()
	// begin = nsel.startContainer.wholeText.substr(0, nsel.startOffset)
	// end = nsel.startContainer.wholeText.substr(nsel.endOffset)
	alert(content.innerHTML)
	// nsel.innerHTML = begin+'<b>'+sel+'</b>'+end;
}

function handler() {
	if(this.readyState == 4 && this.status == 200) {
		// so far so good
		if(this.responseText != null){
			// success!
			document.getElementById(this.reqid).innerHTML = this.responseText
		}else{
		
		}
	} else if (this.readyState == 4 && this.status != 200) {
	}
}


function reset(id) {
	var client = new XMLHttpRequest();
	client.reqid = id
	client.open("DELETE", "/item/"+id);
	client.onreadystatechange = handler;
	client.setRequestHeader("Content-Type", "text/plain;charset=UTF-8");
	client.send();
}

function getSelectionBounds(){
	selObj = window.getSelection().getRangeAt(0);
	index =  selObj.startContainer.parentNode.id
	fromstart = 0
	if (selObj.startContainer.parentNode.tagName!='TD'){
		return null
	}
	if (selObj.startContainer!=selObj.endContainer){
		return null
	}
	currentNode  = selObj.startContainer.previousSibling
	while (currentNode){
		fromstart += currentNode.textContent.length
		currentNode = currentNode.previousSibling
	}
	
	result = new Object()
	result.start = fromstart + selObj.startOffset;
	result.end = fromstart + selObj.endOffset
	result.toString = function(){ return ""+this.start + ':' + this.end}
	return result
}

function mark(tag){
	bounds = getSelectionBounds()
	if (!bounds){
		alert("Wrong selection")
		return
	}
	var client = new XMLHttpRequest();
	client.reqid = selObj.startContainer.parentNode.id
	client.open("POST", "/item/"+client.reqid);
	client.onreadystatechange = handler;
	parameterString = "tag="+tag+"&start="+bounds.start+"&end="+bounds.end
	client.setRequestHeader("Content-type",
        "application/x-www-form-urlencoded");
    client.setRequestHeader("Content-length",
        parameterString.length);
	client.send(parameterString);
}

function recalculateTableSize(){
	tablediv = document.getElementById("tablediv") 
	if (tablediv){
		newheight = (window.innerHeight-90)
		tablediv.style.height=""+(newheight)+"px"
	}
}