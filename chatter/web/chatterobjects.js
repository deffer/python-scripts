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