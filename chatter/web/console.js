/**
 * 
 */

// for IE6
/*if (!window.XMLHttpRequest){
	window.XMLHttpRequest = function() { return new ActiveXObject('Microsoft.XMLHTTP')} 
}*/


// for Opera
if (!Function.prototype.bind){
	Function.prototype.bind=function (context) {		    
	    var __method = this;
	    return function() {
	      return __method.apply(context, arguments);
	    }
	}	
}

// for FireFox
if (!window.console || !window.console.log){
	window.console = {
		log:function(){
			
		}			
	}
}