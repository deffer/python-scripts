function openIconDialog(event){
	console.log("in open dialog: "+event.clientY)
	el = document.getElementById("iconDialog")	
	if (el.style.display==null){
		// not working?
		return	
	}
	el.style.display=null	
	el.style.left=event.clientX+5
	el.style.top=event.clientY+5
	document.body.onclick=onBodyClick
	
	var table = el.getElementsByTagName("table")[0];
	
	for (var i in allicons){
		iconrow = allicons[i]
		var tr=document.createElement("tr")
		var td=document.createElement("td")
		tr.appendChild(td)
		for (var j in iconrow){
			icon = iconrow[j]
			var image = new Image()
			image.type="image/x-png";
			image.style.margin = "0px 0px 0px 0px";
			image.src="/usericons/32/"+icon;
			image.onclick=function (){selectIcon(this);}.bind(icon)
			td.appendChild(image)
		}
		table.appendChild(tr);
	} 
	/*	<tr>
	%for icon in icons:
		<td><img type="image/x-png" style="margin: 0px 0px 0px 0px;" valign="bottom" src="/usericons/32/{{icon}}" 
		onclick="selectIcon('{{icon}}')"/></td>
	%end
	</tr>*/
	
	event.cancelBubble = true;
	if (event.stopPropagation) event.stopPropagation();
}

// cancel iconDialog
function onBodyClick(event){
	el = document.getElementById("iconDialog")
	if (el.style.display=="none"){
		return
	}
	divX = el.offsetLeft
	divY = el.offsetTop
	width = el.clientWidth
	height = el.clientHeight
	x = event.clientX
	y = event.clientY
	console.log("click for "+divX+"("+x+")  "+divY+"("+y+")  "+width+"/"+height) 	
	if (x>divX && x<(divX+width) && y>divY && y<(divY+height)){

	}else{
		document.body.onclick=null
		el.style.display="none"
		console.log("shut down")
	}
}

function showSelectUserNameDialog(){
	console.log("opening username dialog")
	
	el = document.getElementById("userNameDisplaySpan")
	el.style.display="none"
	el = document.getElementById("userNameForm")
	el.style.display=null
	el = document.getElementById("userNameInput")
	el.value = userName=="Chatter"?"":userName
	el.focus();
}

function hideUserName(){
	el = document.getElementById("userNameDisplaySpan")
	el.style.display=null
	el = document.getElementById("userNameForm")
	el.style.display="none"
}

function refreshContactlistUser(user, status, createWhenMissing){
	el = document.getElementById("contactListUser"+user.id);
	if (el==null){
		if (createWhenMissing){
			var ul = document.getElementById("contactList");
			el = document.createElement("li");
			el.id = "contactListUser"+user.id;
			el.style.position="relative";
			ul.appendChild(el); 
		}else{
			return
		}
	}
	el.innerHTML = "";
	
	var image = new Image()
	image.className="contactlistuser";
	image.src="/usericons/32/"+user.icon+"_32.png";
	console.log("binding user "+user.name+"("+user.id+" as "+(typeof user.id)+") to request conversation event");
	image.onclick=(function (){request_conversation(this)}).bind(user.id)
	el.appendChild(image)
	
	var iconStatus = null
	var tooltip = null
	if (status=='havingTalk') {
		iconStatus="/usericons/actions/arrow_medium_lower_left.png";
		tooltip="You are talking with this person";
	}
	if (status=='requestingTalk') {
		iconStatus="/usericons/actions/volume_loud.png";
		tooltip="This person wants to talk to you";
	}
	
	if (iconStatus){		
		image = new Image()
		image.className="imguserstatus";
		image.src=iconStatus;
		image.onclick=(function (){request_conversation(this)}).bind(user.id)
		image.title=tooltip;
		el.appendChild(image)
	}
		
	if (user.online=="False"){		
		image = new Image()
		image.className="imguserstatustop";
		image.src="/usericons/actions/remove.png";
		image.onclick=(function (){request_conversation(this)}).bind(user.id)
		el.appendChild(image)
	}
	
	var span = document.createElement("span");	
	span.innerHTML = user.name;
	el.appendChild(span);
}

function updateContactList(requests){
	for (var i in requests){
		var userid = requests[i] 
		el = document.getElementById("contactListUser"+userid);
		user = getUser(userid)
		if (el==null && user==null){
			// TODO request updating user in contact list
			return
		}	
		
		refreshContactlistUser(user, "requestingTalk", true)
		
	}
	
}

function updateConversations(messages){
	for (var j in messages){
		var key = j
		var talkMessages = messages[j]			
		// add messages to table
		el = $("#historyTable"+key)
		if (el){
			for (var i in talkMessages){
				var msg = talkMessages[i]
				var tr = $("<tr/>").attr({"id":"historyEntry"+msg.id});

				var td = $("<td/>").attr("valign","top").css("font-weight","bold")
				.html(msg.userName+":");
				tr.append(td)

				td = $("<td/>").html(msg.text);				
				tr.append(td)
				el.append(tr);
				console.log("message added "+msg.text)
			}
		
			el = $("#messagesBoard"+key)
			if (el){
				el[0].scrollTop = el[0].scrollHeight;
			}			
		}else{
			console.log("INCONSTISTENCY: cant find history table for conversation "+key)
		}
	}
		
}

function getUser(id){
	for (i in users){
		user = users[i]
		if (user.id==id){
			console.log("    found partner "+user.name+" in local data")
			return user
		}else{
			//console.log("    rejecting "+user.id+"("+user.name+") as not equal to "+id);
		}
	}
	//console.log("_____ unable to find user for id "+id+",  size of users is "+users.length)
}