<table id="conversationTable{{talk.id}}" style="margin: 20px 0px 0px 0px; width:414px;">
	<tr><td>
		<div id="conversationToolbar{{talk.id}}" class="conversationToolbar">
			<img id="toolbarUserIcon{{talk.id}}" class="floatleft" src="/usericons/32/{{partner.icon}}_32.png"></img> 
			<div id="toolbarUserName{{talk.id}}" class="toolbarusername">{{partner.name}}</div>
			<img title="Close conversation" class="toolbarbutton" src="/usericons/actions/close_small_16.png"
				onclick="closeConversation('{{talk.id}}')"></img>
			<img title="Send file" class="toolbarbutton" src="/usericons/actions/send_file_16.png"></img>
		</div>
	</td></tr>
	
	<tr><td>
		<div id="messagesBoard{{talk.id}}" 
			style="max-height:140px; max-width:412px; background-color:#ffffff; overflow:auto; 
			       border-style:solid; border-width:1px; border-color:#CCC;">
		<table id="historyTable{{talk.id}}">
			%for msg in talk.messages:
				%print msg.type			
				%if msg.type=='n':
				<tr id="historyEntry{{msg.id}}"><td valign="top" style="font-weight:bold;">{{msg.user.name}}:</td>
				<td><div class="messagecell">{{msg.text}}</div></td></tr>
				%end
			%end
		</table>
		</div>
	</td></tr>
			
	<tr><td>
		<textarea id="input{{talk.id}}" rows="4" cols="49" style="font-size: 13px;"
			onkeydown="if (event.keyCode==13 && event.ctrlKey){sendMessage('{{talk.id}}')}"></textarea>   
	</td></tr>
	
	<tr><td>
		<button class="floatright" onclick="sendMessage('{{talk.id}}')">Send</button>
		<div id="statusMsg{{talk.id}}" class="floatleft">
		%if not talk.acceptedBy(partner.id):
			*This conversation is not accepted yet
		%end
		</div>
	</td></tr>
		
</table>