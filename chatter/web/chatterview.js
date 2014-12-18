function openIconDialog(event){
	console.log("in open dialog: "+event.clientX+":"+event.clientY)
	el = $("#iconDialog")	
	
	el.css("display", "").css("left", event.clientX+5).css("top", event.clientY+5);
	$("body").click(onBodyClick);

	if (!el.data("loaded")){

		var table = el.find("table");
	
		for (var i in allicons){
			iconrow = allicons[i]
			var tr = $("<tr/>")
			var td = $("<td/>")
			tr.append(td)
			for (var j in iconrow){
				icon = iconrow[j]
				var image = $("<img/>")
				image.attr("type", "image/x-png").css("margin", "0px 0px 0px 0px").attr("src", "/usericons/32/"+icon);
				image.click(function (){selectIcon(this);}.bind(icon));
				td.append(image)
			}
			table.append(tr);
		}
		el.data("loaded", true);
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
		//document.body.onclick=null
		$("body").click(onBodyClick);
		el.style.display="none"
		//console.log("shut down")
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
	
	var userimage;
	var li = $("#contactListUser"+user.id);
	if (li.length==0){
		if (createWhenMissing){
			var ul = $("#contactList");
			li = $("<li/>").attr({"id":"contactListUser"+user.id}).css("position", "relative");
			ul.append(li);
			
			userimage = $("<img/>").addClass("contactlistuser");
			userimage.attr("src", "/usericons/32/"+user.icon+"_32.png");
			userimage.click(function (){requestConversation(this)}.bind(user.id));
			console.log("binding contact list user "+user.name+" to request conversation event");
			li.append(userimage)			
		}else{
			return
		}
	}else{
		userimage = li.find('img.contactlistuser').attr("src", "/usericons/32/"+user.icon+"_32.png");
	}

	
	console.log(status)
	var statusimage = li.find('img.imguserstatus');
	
	if (status){			
		if (statusimage.length==0){
			statusimage = $("<img/>").addClass("imguserstatus");
			statusimage.attr({"src":status.iconStatus, "title":status.tooltip});
			userimage.attr({"title":status.tooltip});	
			if (status==REQUESTING_TALK){
				statusimage.data("blinking", true);
				var dd = user.id
				setTimeout(function (){blinking(dd)}, 500);
			}
			statusimage.click(function (){requestConversation(this)}.bind(user.id))
			li.append(statusimage)
		}else if (status.iconStatus != statusimage.attr("src")){
			// start/stop blinking
			if (status==REQUESTING_TALK){
				statusimage.data("blinking", true);
				blinking(user.id);
			}else if (statusimage.attr("src")==REQUESTING_TALK.iconStatus){
				console.log("cancelling blinking")
				statusimage.data("blinking",false);
				statusimage.css("display","");
			}
			statusimage.attr({"src":status.iconStatus, "title":status.tooltip});
			userimage.attr({"title":status.tooltip});
		}
	}else {
		statusimage.data("blinking",false)
		statusimage.remove();
		userimage.attr({"title":""});
	}
		
	var statusimagetop = li.find('img.imguserstatustop');
	if (user.online=="False" || user.online=="false"){
		if (statusimagetop.length==0){
			statusimagetop = $("<img/>").addClass("imguserstatustop");
			statusimagetop.attr({"src":"/usericons/actions/remove.png"});
			statusimagetop.click(function (){requestConversation(this)}.bind(user.id));
			li.append(statusimagetop)
		}
	}else{
		statusimagetop.remove();		
	}
	
	var span = li.find('span');
	if (span.length==0){
		span = $("<span/>").html(user.name);
		li.append(span);
	}else{
		span.html(user.name);
	}	
}

function blinking(userid){
	//console.log('blinking called')
	var li = contactListElement.find("#contactListUser"+userid);
	if (li.length==0){
		//console.log("#contactListUser"+userid+"  is not found")
		return
	}
	var statusimage = li.find('img.imguserstatus');
	/*if (statusimage.length==0){
		console.log("#img.imguserstatus for "+userid+"  is not found")
	}*/
	if (statusimage.data("blinking")){
		statusimage.toggle();
		setTimeout(function(){blinking(userid)}, 500);
	}/*else{
		console.log("#img.imguserstatus for "+userid+"  is not blinking")
	}*/
}

function updateContactList(requests, clusers){
	// update users with request flag
	for (var i in clusers){
		userstatus = null;
		cluser = clusers[i]
		//console.log(cluser.id)
		//console.log(requests)
		if($.inArray(cluser.id, requests) > -1){
			userstatus = REQUESTING_TALK			
		}else if (havingTalkWith(cluser.id)){
			userstatus = HAVING_TALK
		}
		var user = getUser(cluser.id)
		if (!user){
			console.log("    creating local user "+cluser.name)
			user = new User(cluser.id, cluser.icon,  cluser.name, "", ""+cluser.online)			
			users.push(user)
		}else{
			user.name = cluser.name;
			user.icon = cluser.icon;
			user.online = ""+cluser.online;
		}
		refreshContactlistUser(user, userstatus, true)
		user.status = userstatus
	}
		
}

function updateConversation(messages, talk){	
	var el = $("#historyTable"+talk.id)
	if (el.length==0){
		console.log("INCONSTISTENCY: cant find history table for conversation "+key);
		return;
	}
	
	// add messages to table
	for (i in messages){
		var msg = messages[i]
		var tr = $("<tr/>").attr({"id":"historyEntry"+msg.id});

		if (msg.type=='n'){
			var td = $("<td/>").attr("valign","top").css("font-weight","bold")
				.html(msg.userName+":");
			tr.append(td)
		
			td = $("<td/>").append($("<div/>").addClass("messagecell").html(
				msg.text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g, '<br>')));
		}else if (msg.type=='s' && msg.userid!=currentUser.id){
			// td.css("color", "red").css("font-style","italic")
			//var statusEl = el.find("#statusMsg"+talk.id);
			var statusEl = $("#statusMsg"+talk.id);
			if (statusEl.length==0){
				console.log("can't find element statusMsg"+talk.id);
			}
			if (msg.text.indexOf("DECLINED")>=0){
				console.log("DECLINED");
				statusEl.css("color", "red").css("font-style","italic");
				statusEl.text("User declined your request for conversation");
			}else if (msg.text.indexOf("ACCEPTED")>=0){
				console.log("ACCEPTED");
				statusEl.text("");
			}else if (msg.text.indexOf("CLOSED")>=0){
				console.log("CLOSED");
				statusEl.css("color", "red").css("font-style","italic");
				statusEl.text("User closed this conversation");
			}else{
				console.log("Unknown status message: "+msg.text);
			}			
		}
		tr.append(td)
		el.append(tr);
		
		talk.lastMsgId = msg.id
		console.log("message added "+msg.text)			
	}
	el = $("#messagesBoard"+talk.id);
	el[0].scrollTop = el[0].scrollHeight;	
} 


function updateConversations(messages){
	for (var key in messages){		
		var talk = conversations[key]
		if (!talk){
			console.log("INCONSTISTENCY: cant find conversation object "+key);
			return;
		}
		
		var talkMessages = messages[key]
		updateConversation(talkMessages, talk);		
	}
		
}

function getUser(id){
	for (i in users){
		user = users[i]
		if (user.id==id){
			//console.log("    found user "+user.name+" in local data")
			return user
		}
	}
	//console.log("_____ unable to find user for id "+id+",  size of users is "+users.length)
}

function havingTalkWith(partnerid){
	for (i in conversations){
		c = conversations[i]
		if (c.partner ==  partnerid){
			return true
		}
	}
}