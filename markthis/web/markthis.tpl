<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>MarkThis!</title>
<link rel="stylesheet" type="text/css" href="/styles/markthis.css" /> 
<style type="text/css">
%for tag in validTags:
.{{tag.name}}{background-color:{{tag.background}};}
%end
</style>
<script src="/scripts/shortcut.js">
</script>
<script src="/scripts/markthis.js">
</script>
<script>
%for tag in validTags:
%if tag.key!='':
shortcut.add("{{tag.key}}",function() {
	mark('{{tag.name}}')
});
%end
%end
</script>
</head>
<body onload="recalculateTableSize()" onresize="recalculateTableSize()">
%if len(items)>0:
<div id="tablediv" style="overflow:auto; margin-bottom:10px" class="indented">
<table id="itemsTable" name="mainTable" >
<thead><tr>
<th>Reset</th><th>Item</th>
</tr></thead>
<tbody>
%for item in items:
	<tr >
	<td class="first-column"><a href="#" onclick = {{'"reset(' + str(item.index) + '); return false"'}}>{{str(item.index)}}</a></td>
    <td id ={{'\'' + str(item.index) + '\''}}>{{!item.getInnerHTML()}}</td>
	</tr>
%end
</tbody></table>
</div>
<div class="indented">
<div name="titlesbar">
%for tag in validTags:
<a href="#" class="{{tag.name}}" 
	onclick = "mark('{{tag.name}}');return false">{{tag.name.title() +(' ['+tag.key+']' if tag.key!='' else '')}}</a>
%end
</div>
<div>
<a href="/result">Show result</a>
<a href="/result/result.txt">Save result</a>
</div>
%else:
<div class="indented">
No source file uploaded. Please upload a new one!
%end

<div>
<form action="/source" method="post" enctype="multipart/form-data" accept="text/plain; charset=UTF-8" accept-charset="UTF-8">
Type (or select) Filename: 
<input type="file" name="datafile">
<input type="submit" value="Upload">
</form>
</div>
</div>
</body>
</html>