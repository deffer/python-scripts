$("#loading").bind("ajaxError", function(request, status, err){
   $(this).show();
   clearTimeout(timer)	
   console.log("Timers stopped");
   //timer=setTimeout('startTime()',30000)
 });

function startTime(){
	timer=setTimeout('startTime()',30000);
	ping()	
}

function request_conversation_old(userid){
	if (userid==currentUser.id){
		return
	}
	var client = new XMLHttpRequest();
	client.open("POST", "/request.do", true);
	client.onreadystatechange = requestConversationHandler;
	parameterString = "partnerid="+userid
	client.partnerid=userid
	client.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	client.send(parameterString);
}


function request_conversation(userid){	
	if (userid==currentUser.id){
		return
	}
	console.log("request conversation with "+userid+" typeof "+(typeof userid))  
	// number for index-generated
	// object for script generated
	$.ajax({
	    url: "request.do",
	    type: "POST",
	    data: ({partnerid : ""+userid}),
	    //data: "name=John&location=Boston",
	    dataType: "json",    
	    success: function(data){
	    	request_conversationHandler(data, userid)
	    }	
	})
}

function request_conversationHandler(result, partnerid){
	console.log("Handling conversation response: "+result)
	console.log("Handling conversation with partner: "+partnerid)
	if (!result.msg){
		lastMsgId = result.msgId
		console.log("userid type is "+(typeof result.myid))
		setNewUserId(result.myid)
		var talkid = result.talkid
		el = document.getElementById("input"+talkid)
		if (el){
			el.focus()
			return
		}
		console.log("    setting msgId="+lastMsgId+" for user "+userId)				
		el = document.getElementById("divConversations")
		var oldHTML = el.innerHTML
		el.innerHTML = oldHTML+'\n'+result.html
		el.style.visibility=null
		el.style.width=null

		// update contactlist icon
		console.log("    getting partner for id "+partnerid)
		refreshContactlistUser(getUser(partnerid), "havingTalk", false)
	}	
}


function requestConversationHandler(){
	console.log("Handling conversation response")
	if(this.readyState == 4 && this.status == 200) {
		if(this.responseText != null){		
			// success!
			result = eval("("+this.responseText+")")
			if (result.msg){
			}else{
				lastMsgId = result.msgId
				setNewUserId(result.myid)
				var talkid = result.talkid
				el = document.getElementById("input"+talkid)
				if (el){
					el.focus()
					return
				}
				console.log("    setting msgId="+lastMsgId+" for user "+userId)				
				el = document.getElementById("divConversations")
				var oldHTML = el.innerHTML
				el.innerHTML = oldHTML+'\n'+result.html
				el.style.visibility=null
				el.style.width=null
				
				// update contactlist icon
				console.log("    getting partner for id "+this.partnerid)
				refreshContactlistUser(getUser(this.partnerid), "havingTalk", false)
			}
		}else{}
	} else if (this.readyState == 4 && this.status != 200) {}
}

function selectIcon(name){		
	// extract icon name
	myregexp = /(.+)_32\.png/
	mymatch = myregexp.exec(name)
	m = mymatch[1]
	console.log("selected "+name+"   name is "+m)
	
	// set to fields
	/*el = document.getElementById("currentIconName")
	el.value = m*/
	currentUser.icon = m
	el = document.getElementById("currentIconImage")
	el.style.backgroundImage="url(/usericons/48/"+m+"_48.png)"
	
	// close dialog
	document.body.onclick=null
	el = document.getElementById("iconDialog")
	el.style.display="none"
	console.log("shut down")
	
	// call server
	var client = new XMLHttpRequest();
	client.open("POST", "/usericon.do");
	client.onreadystatechange = updateUserIdHandler
	parameterString = "iconname="+m
	client.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	client.send(parameterString);
}

function confirmUserName(){
	userName = document.getElementById("userNameInput").value
	currentUser.name = userName
	console.log("userName: " + userName)
	document.getElementById("userNameDisplaySpan").innerHTML = userName
	document.title=userName
	hideUserName()
	
	// send to teh server
	var client = new XMLHttpRequest();
	client.open("POST", "/username.do");
	client.onreadystatechange = updateUserIdHandler
	parameterString = "userName="+userName
	client.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	client.send(parameterString);
}

function updateUserIdHandler(){
	console.log(this.responseText)
	if(this.readyState == 4 && this.status == 200) {
		if(this.responseText != null){		
			result = eval("("+this.responseText+")")			
			if (result.myid){				
				if (userId != result.myid){
					console.log("replacing old id "+userId+" with new "+result.myid)
					setNewUserId(result.myid)					
				}
				refreshContactlistUser(currentUser, null, true)
			}
		}else{}
	} else if (this.readyState == 4 && this.status != 200) {}
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

function sendMessage_old(talkid, event){
	el = document.getElementById("input"+talkid)
	message = el.value	
	el.focus()
	if (message==null || message==""){
		return
	}
	var client = new XMLHttpRequest();
	client.open("POST", "/message.do");
	client.onreadystatechange = sendMessageHandler
	client.talkid=talkid
	parameterString = "talkid="+talkid+"&lastMsgId="+lastMsgId+"&message="+escape(message)
	console.log(parameterString)
	client.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	client.send(parameterString);
}

function sendMessage(talkid){
	
	el = $("#input"+talkid).focus()
	message = el.val()	
	if (message==null || message==""){
		console.log("empty message");
		return
	}

	$.post("message.do",
		{"lastMsgId" : ""+lastMsgId,
		"talkid" : ""+talkid,
		"message": message},
		function(data){
			sendMessageHandler(data, talkid)
		}, "json")
}

function sendMessageHandler(result, talkid){
	console.log("Handling message sent");
	console.log(result)
	if (result.msg==null){
		// remember time
		lastTime = result.newTime
		lastMsgId = result.newMsgId

		// add messages to table
		el = $("#historyTable"+talkid)
		for (i in result.messages){
			var msg = result.messages[i]
			var tr = $("<tr/>").attr({"id":"historyEntry"+msg.id});

			var td = $("<td/>")
				.attr("valign","top")
				.css("font-weight","bold")
				.html(msg.userName+":");
			tr.append(td)

			td = $("<td/>").html(msg.text);				
			tr.append(td)
			el.append(tr);
			console.log("message added "+msg.text)
		}
		el = $("#messagesBoard"+talkid);
		el[0].scrollTop = el[0].scrollHeight;			

		el = document.getElementById("input"+talkid)
		el.value=""
	}
}


function ping(){
	console.log("Pinging with "+lastMsgId+" typeof "+(typeof lastMsgId))
	$.post("ping.do",
	    {"lastMsgId" : ""+lastMsgId},
	    function(data){
	    	pingHandler(data, lastMsgId)
	 }, "json")
}

function pingHandler(result, prevMsgId){
	if (timer){
		clearTimeout(timer)	
	}
	
	console.log("Handling ping response for "+prevMsgId)
	if (result.msg){
		console.log("Server responds: "+result.msg)
	}else if (!result.newMsgId){
		console.log("Empty respond");
	}else{
		lastMsgId = result.newMsgId
		lastTime = result.newTime

		console.log(result)
		updateConversations(result.messages)
		updateContactList(result.requests)
	}
	timer=setTimeout('startTime()',5000);
}





