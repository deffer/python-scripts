$(document).ajaxError(function(event, request){
	//$(this).show();
	clearTimeout(timer)	
	console.log("Timers stopped");
	//timer=setTimeout('startTime()',30000)

	if (!request.responseText){
		$('#errorMessageArea').html("Server is offline");
	}else{
		$('#errorMessageArea').html(request.responseText);
	}
	
	el =  $('#errorDialog')
	var w = el.width();
	var h = el.height();
	el.css('margin-left', -w/2).css('margin-top', -h/2);
	el.show();
});

function startTime(){
	timer=setTimeout('startTime()',30000);
	ping()	
}


function requestConversation(userid){	
	if (userid==currentUser.id){
		return
	}
	console.log("request conversation with "+userid+" typeof "+(typeof userid))  
	// number - from index-generated
	// object - from script generated
	$.ajax({
	    url: "request.do",
	    type: "POST",
	    data: ({partnerid : ""+userid}),
	    dataType: "json",    
	    success: function(data){
	    	requestConversationHandler(data, userid)
	    }	
	})
}

function requestConversationHandler(result, partnerid){
	//console.log("Handling conversation response: "+result)
	//console.log("Handling conversation with partner: "+partnerid)
	if (!result.msg){
		//lastMsgId = result.msgId
		setNewUserId(result.myid)
		console.log("Conversation Handler: setting msgId="+result.msgId+" for user "+userId)		
		var talkid = result.talkid
		console.log("    getting partner for id "+partnerid)
		var partner = getUser(partnerid)		
		conversations[talkid] = new Conversation(talkid, partner, result.msgId)
		
		el = $("#input"+talkid)
		if (el.length==0){			
							
			var div = $("#divConversations")
			var oldHTML = div.html()
			div.html(oldHTML+'\n'+result.html)
			div.css("visibility", "").css("width", "");			

			// update contactlist icon
			refreshContactlistUser(partner, HAVING_TALK, false)
			partner.status = HAVING_TALK
			
			// for further set focus
			el = $("#input"+talkid)
		}
		if (el){
			el.focus()
		}
	}	
}


function selectIcon(name){		
	// extract icon name
	myregexp = /(.+)_32\.png/
	mymatch = myregexp.exec(name)
	m = mymatch[1]
	console.log("selected "+name+"   name is "+m)
	
	// set to fields
	currentUser.icon = m
	el = document.getElementById("currentIconImage")
	el.style.backgroundImage="url(/usericons/48/"+m+"_48.png)"
	
	// close dialog
	document.body.onclick=null
	el = document.getElementById("iconDialog")
	el.style.display="none"
	console.log("shut down")
	
	$.post("usericon.do",
	    {"iconname" : ""+m},   
	    function(data){
	    	updateUserIdHandler(data)
	    }, "json"	
	)
}

function confirmUserName(){
	el = $("#userNameInput");
	userName = el.val();
	currentUser.name = userName
	console.log("userName: " + userName);
	
	el = $("#userNameDisplaySpan")
	el.html(userName);
	document.title=userName
	hideUserName()
	
	$.post("username.do",
	    {"userName" : ""+userName},   
	    function(data){
	    	updateUserIdHandler(data)
	    	console.log("Username has changed");   	
	    }, "json"	
	)
}


function updateUserIdHandler(result){
	
	if (result.myid){				
		if (userId != result.myid){
			console.log("replacing old id "+userId+" with new "+result.myid)
			setNewUserId(result.myid)					
		}
		//refreshContactlistUser(currentUser, null, true)
	}

}

function setNewUserId(newUserId){
	userId = newUserId
	if (currentUser.id!=newUserId){
		currentUser.id = newUserId
		if (!getUser(newUserId)){
			users.push(currentUser);
		}		
	}
}


function sendMessage(talkid){
	
	el = $("#input"+talkid).focus()
	message = el.val()	
	if (message==null || message==""){
		console.log("empty message");
		return
	}

	$.post("message.do",
		{"lastMsgId" : ""+conversations[talkid].lastMsgId,
		"talkid" : ""+talkid,
		"message": message},
		function(data){
			sendMessageHandler(data, talkid)
		}, "json")
}

function sendMessageHandler(result, talkid){
	console.log("Handling message sent");
	console.log(result)
	
	var talk = conversations[talkid]
	if (!talk){
		console.log("INCONSTISTENCY: cant find conversation object "+key);
		return;
	}
	
	if (result.msg==null){
		// remember time
		lastTime = result.newTime

		// add messages to table
		updateConversation(result.messages, talk);
				
		/*el = $("#historyTable"+talkid)
		for (i in result.messages){
			var msg = result.messages[i]
			var tr = $("<tr/>").attr({"id":"historyEntry"+msg.id});

			var td = $("<td/>")
				.attr("valign","top")
				.css("font-weight","bold")
				.html(msg.userName+":");
			tr.append(td)

			td = $("<td/>").append($("<div/>").addClass("messagecell").html(
					msg.text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g, '<br>')));				
			tr.append(td)
			el.append(tr);
			
			talk.lastMsgId = msg.id
			console.log("message added "+msg.text)			
		}
		el = $("#messagesBoard"+talkid);
		el[0].scrollTop = el[0].scrollHeight;*/			

		el = document.getElementById("input"+talkid)
		el.value=""
	}
}


function ping(){
	//console.log("Pinging with "+lastMsgId+" typeof "+(typeof lastMsgId))
	var mapp = {}
	var pingId = '';
	for (var i in conversations){
		c =conversations[i]
		//console.log("Pinging with talk message "+c.lastMsgId+" (i="+i+")");
		if (pingId!='') pingId+=', ';
		pingId+=c.lastMsgId
		mapp[""+c.id] = ""+c.lastMsgId;
	}
	if (pingId!=''){
		console.log("Pinging with talk message(s) "+pingId)
	}

	$.post("ping.do",
	    {"conversations": JSON.stringify(mapp),
		"lastTime": ""+lastTime},
	    function(data){
	    	pingHandler(data, pingId)
	 }, "json")
}

function pingHandler(result, pingId){
	if (timer){
		clearTimeout(timer)	
	}
		
	if (pingId!='') pingId=" for "+pingId;
	if (result.msg){
		console.log("Handling ping response"+pingId+": "+result.msg);
	}else if (!result.messages){
		console.log("Handling ping response"+pingId+": EMPTY");
	}else{
		if (result.userchanges.length>0){
			summary = ": "+result.userchanges.length+" changed users";
		}else {summary="";}
		console.log("Handling ping response"+pingId+summary)
		
		lastTime = result.newTime

		//console.log(result)
		updateConversations(result.messages)
		updateContactList(result.requests, result.userchanges)
	}
	timer=setTimeout('startTime()',5000);
}

function pingTime(){
	console.log("Pinging server for time elapsed from "+lastTime);
	$.post("ping.do",
	    {"gettime" : ""+lastTime},
	    function(data){
	    	oldtime = parseInt(lastTime)
	    	newtime = parseInt(data['newTime'])
	    	delta = newtime-oldtime
	    	console.log("  Time difference is "+delta+" (server time is "+newtime+")");
	    	if (delta>1000*60*60*2){
	    		window.location.reload();	    		
	    	}
	    }, "json")
}

function closeConversation(talkid){
	$.post("close.do",
		 {"talkid" : ""+talkid},
		 function(data, code, req){
			 if (data && data.msg) console.log(data.msg);
			 el = $("#conversationTable"+this)
			 console.log("Searching element conversationTable"+this)
			 if (el.length>0){
				 // remove conversation view
				 console.log("Removing element")
				 el.remove()
			 }
			 var c = conversations[talkid]
			 if (c){
				 // remove local object
				 delete(conversations[talkid]);
				 
				 // update partner's icon in contact list
				 var partner = c.partner;
				 refreshContactlistUser(partner, null, false);
			 }
			 			 
		 }.bind(talkid), "json")
}



