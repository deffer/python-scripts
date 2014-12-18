<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<title>{{result.name}}</title>
	<link rel="stylesheet" type="text/css" href="/styles/chatter.css" /> 
	<link rel="icon" type="image/png" href="/usericons/favicon.png">
	<style type="text/css">
		body {margin:0 0 0 0; padding:0;}
	</style>
	<script src="/scripts/jquery-1.4.4.min.js.gz" type="text/javascript"></script>
	<script src="/scripts/console.js" type="text/javascript"></script>
	<script src="/scripts/chatterobjects.js" type="text/javascript"></script>
	<script src="/scripts/chatter.js" type="text/javascript"></script>	
	<script src="/scripts/chatterview.js" type="text/javascript"></script>	
	<script type="text/javascript">
		$(document).ready(function() {
			timer=setTimeout('startTime()',5000);
		 });
	
		currentUser = new User("{{result.id}}", "{{result.icon}}", "{{result.name}}", "{{result.country}}", "result.online")
		userName = "{{result.name}}"
		userId = "{{result.id}}"
							
		lastTime = {{lastTime}}
		lastMsgId = {{lastMsgId}}
		timer = null
		
		users = []	
		allicons = []
		
		%for user in onliners:
			%if (user.id==result.id):
				users.push(currentUser)
			%else:
				var user = new User("{{user.id}}", "{{user.icon}}",  "{{user.name}}", "", "{{user.online}}")
				users.push(user)
			%end
		%end 		
		
		%for icons in allIcons:
			iconrow = []
			%for icon in icons:
				iconrow.push("{{icon}}")
			%end
			allicons.push(iconrow)
		%end
	</script>
</head>

<body style="margin: 0px; padding: 0px;" background="/usericons/24original.gif">
<div id="page" style="margin-left:auto; margin-right:auto; width:700px; 
	background:white; border-left:1px solid #ffcc19; border-right:1px solid #ffcc19;">

<div style="position:relative;">

<div id="header" style="margin-left:20px; padding-bottom:20px; height:70px;">
	<div style="float:left; height:54px; width:52px;">
	<div id="currentIconImage" style="background-image: url(/usericons/48/{{result.icon}}_48.png); 
		width: 42px; height:43px;margin: 10px 10px 1px 0px;" 
		onclick="return openIconDialog(event)"></div> 
    </div>		  	
  <div id="username_area" style="float:left; margin-top:26px;  padding: 0px 0px 0px 0px; height:54px; text-align:center;">
  	<div style="float:left; margin-top:10px;">Your name is</div>
	<div id="userNameDisplaySpan" class="usernamespan" 
		style="float:left; margin:10px 0px 0px 10px;" onclick="showSelectUserNameDialog()"> 
		{{'not set' if result.name=='Chatter' else result.name}}
	</div>
	<div id="userNameForm" style="float:left; display:none; width:260px;">
		<table><tr>
		<td><input id="userNameInput" type="text"></input></td>		
  		<td><div class="buttonimg" style="float:right; height:32px; width:32px; background-image: url(/usericons/actions/Checked.png)" 
  			onclick="confirmUserName()"></div>
  		</td><td>
			<div class="buttonimg" style="float:right; height:32px; width:32px; background-image: url(/usericons/actions/Delete.png)" 
  				onclick="hideUserName()"></div>
  		</td></tr></table>  			
	</div>
  </div>

	<div class="buttonimgblue" style="height:32px; width:32px; margin: 10px 15px 0px 0px; float:right; background-image: url(/usericons/actions/Blue_Play.png)" 
		id="iconResume" onclick="timer=setTimeout('startTime()',5000)" title="DEBUG: resume refresh"></div>
	<div class="buttonimgblue" style="height:32px; width:32px; margin: 10px 0px 0px 0px; float:right; background-image: url(/usericons/actions/Blue_Pause.png)" 
		id="iconPause" onclick="clearTimeout(timer)" title="DEBUG: stop refresh"></div>   			  

</div>
</div>


<div id="body" style="background:white; width:100%; height:900px;">
<div id="body_all" style="width:660px; background:white; padding:0px 0px 40px 20px; overflow:hidden;">
<div id="body_left" style="width:auto; height:auto; float:left; margin:0px 0px 0px 0px; 
	padding-left:15px; padding-right:15px;">
	<div id="divConversations"  style="
	%if len(talks)==0:
		visibility:hidden;
	%end
	min-width:420px;
	min-height:400px;">
	%for talk in talks:	
		%include conversation talk=talk,lastTime=lastTime
	%end
	</div>
</div>
<div id="body_right" style="width:200px; float:right; background:white; margin-top:20px;">
	<ul style="list-style-type:none; margin:0px 0px 0px 0px;" id="contactList" >
		%partners = list()
		%for talk in talks:
			%partnerId = talk.getMyPartner(result.id).id
			%print "detecting partner", partnerId
			%partners+=[partnerId]
		%end
		%for user in onliners:
			%marginleft = "0"
			%print 'adding to contact list', user.id, '(', user.name,')'
			<li id="contactListUser{{user.id}}" style="position:relative;"> 
				<img class="contactlistuser" src="/usericons/32/{{user.icon}}_32.png" 
				onclick="request_conversation({{user.id}})"/>
				%if user.id in partners:
					%marginleft="18"
					<img class="imguserstatus" src="/usericons/actions/arrow_medium_lower_left.png" 
					onclick="request_conversation({{user.id}})"/>
				%end
				%if user.online==False:
					%marginleft="18"
					<img class="imguserstatustop" src="/usericons/actions/remove.png" 
					onclick="request_conversation({{user.id}})"/>
				%end				
				
				<span>{{user.name}}</span>
			</li>
			
		%end
	</ul>
</div>
</div>
</div>


<div id="iconDialog" style="position:absolute; left:500px; top:100px; display:none; background:white; border:1px solid;">
<table>
</table>
</div>

</div>
</body>
</html>