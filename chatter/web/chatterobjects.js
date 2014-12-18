/**
 * 
 */

User = function(id, icon, name, country, online){
	this.id = id;
	this.icon = icon;
	this.name = name;
	this.country = country;
	this.online = online;
	console.log("new user created "+id+" ("+name+")");			
}

Conversation = function(id, partner, lastMsgId){
	this.id = id;
	this.partner = partner;
	this.lastMsgId = lastMsgId
}

HAVING_TALK={
	iconStatus:"/usericons/actions/arrow_medium_lower_left.png",
	tooltip:"You have opened conversation with this person"
};

REQUESTING_TALK={
	iconStatus:"/usericons/actions/volume_loud.png",
	tooltip:"This person wants to talk to you. Click to accept."
};
