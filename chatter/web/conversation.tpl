<table id="conversationTable{{talk.id}}" style="margin: 20px 0px 0px 0px; width:414px;">
	<tr><td>
		<div id="messagesBoard{{talk.id}}" 
			style="max-height:140px; background-color:#ffffff; overflow:auto; 
			       border-style:solid; border-width:1px; border-color:#CCC;">
		<table id="historyTable{{talk.id}}">
			%for msg in talk.messages:
				<tr id="historyEntry{{msg.id}}"><td valign="top" style="font-weight:bold;">{{msg.userName}}:</td>
				<td>{{msg.text}}</td></tr>
			%end
		</table>
		</div>
	</td></tr>
			
	<input type="hidden" name="talkid" value="{{talk.id}}"></input>	
	<tr><td>
		<textarea id="input{{talk.id}}" rows="4" cols="49"
			onkeydown="if (event.keyCode==13 && event.ctrlKey){sendMessage({{talk.id}})}"></textarea>   
	</td></tr>
	
	<tr><td align="right">
		<button onclick="sendMessage({{talk.id}})">Send</button>
	</td></tr>
		
</table>