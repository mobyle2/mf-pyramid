<%inherit file="layout.mako"/>

<ul class="nav nav-tabs">
  <li class="active">
    <a href="#" id="dashboard" class="dashboard-item">Dashboard</a>
  </li>
  % for object in objects:
  <li><a href="#" class="dashboard-item" id="${object}">${object}s</a></li>
  % endfor
</ul>
<div id="mf-flash" class="mf-flash"></div>

<div id="dashboard" class="mf-dashboard mf-list">


</div>

% for object in objects:
<div id="list-${object}" class="mf-list">
  <table class="mf-table table table-hover" id="table-${object}">
  </table>
</div>
% endfor
<hr/>
% for object in klasses:
<div class="row">

<div class="accordion offset1" id="accordion${object.__name__}">
<div class="accordion-group">
<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion${object.__name__}" href="#show-${object.__name__}"><h2>${object.__name__}</h2></a></div>
<div id="show-${object.__name__}" class="mf-object offset1 accordion-body collapse in">
  ${object().render() | n}
</div>
<div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion${object.__name__}" href="#search-${object.__name__}"><h2><i class="icon-search"></i> Search</h2></a></div>
<div id="search-${object.__name__}" class="mf-search offset1">
  ${object().render_search() | n}
</div>

</div>
</div>


</div>
% endfor

</div>

<script>



   var curObject;

   var count=0;

   var objList = {};

   var autocompleteelt = null;

$(document).ready(function() {

   $(".mf-list").hide();
   //$(".mf-object").hide();
   $(".accordion").hide();
   //$(".mf-search").hide();
   $(".mf-template").hide();
   $(".dashboard-item").click(function(event){
     $('.nav li').removeClass('active');
     var $this = $(this).parent();
     if (!$this.hasClass('active')) {
       $this.addClass('active');
     }
     object = event.target.id;
     curObject = object
     if(object=="dashboard") {
       $(".mf-list").hide();
       $(".accordion").hide();
       $(".mf-search").hide();
       $("#dashboard").show();
    $("#accordion"+curObject).show();
     }
     else {
       loadObjectList(object);
     }
   });

   $(document).on("click", ".mf-list-object", function(event) {
     object = $(event.target).parent().attr("id");
     loadObject(object);
   });

   $(document).on("click", ".mf-clear-object", function(event) {
     object = $(this).attr("data-dbref");
     object = object.replace(/\[/g,'\\[');
     object = object.replace(/\]/g,'\\]');
     $('#'+object).val('');
     $('#DbRef'+object).val('');     
   });

   $(document).on("click", ".mf-del", function(event) {
    var obj = $(this).attr('elt');
    arrayelts = $('#'+obj);
    if(arrayelts.size()==1) { alert("Cannot delete this element, list must contain at least one (possibly empty) parameter"); }
    else { $(this).parent().remove();}
   });


   $('.mf-dbref').typeahead({
      source: function (query, process) { return getObjects(query,$(this)[0].$element[0].dataset.dbref,$(this)[0].$element[0].dataset.object,process);},
      updater: function (item) { $("#"+autocompleteelt).val(objList[item]);return item;},
      minLength: 3 
   });


/*
   $('body').typeahead({
      selector: '[.mfdbref]',
      source: function (query, process) { return getObjects(query,$(this)[0].$element[0].dataset.dbref,$(this)[0].$element[0].dataset.object,process);},
      updater: function (item) { $("#"+autocompleteelt).val(objList[item]);return item;},
      minLength: 3 
   });
*/
   


   $('.mf-add').click(function(event) {
    var obj = $(this).attr('elt');

    obj = obj.replace(/\[/g,'\\[');
    obj = obj.replace(/\]/g,'\\]');

    arrayelts = $('#Template'+obj);
    template = $(arrayelts[0]).children();
          
    clonediv = $('#Clone'+obj);
    newelt = template.clone();
    inputs = newelt.find('input:not(.mf-dbref)');
    $.each(inputs, function(input) {
        elt = $(inputs[input])
        oldid = elt.attr("id");
        elt.attr("id",oldid+'['+count+']');
        elt.attr("name",oldid+'['+count+']');
        elt.val();
        dbrefobj = oldid.replace(/\[/g,'\\[');
    	dbrefobj = dbrefobj.replace(/\]/g,'\\]');
    	newdbref = newelt.find("#DbRef"+dbrefobj);
        if(newdbref!=null) {
        newdbref.attr("data-dbref",oldid+'['+count+']');
        newdbref.attr("id","DbRef"+oldid+'['+count+']');
        newdbrefclear = newelt.find("#DbRefClear"+dbrefobj);
        newdbrefclear.attr("data-dbref",oldid+'['+count+']');
        newdbrefclear.attr("id","DbRef"+oldid+'['+count+']');
        }
    });
    //oldid = newelt.find('input:not(.mf-dbref)').attr("id");
    //newelt.find('input:not(.mf-dbref)').attr("id",oldid+count);
    //newelt.find('.mf-dbref').attr("data-dbref",oldid+count);
    count++; 
    //newelt.find('input:not(.mf-dbref)').val('');
    clonediv.append(newelt);
    
    newelt.find('.mf-dbref').typeahead({
          source: function (query, process) { return getObjects(query,$(this)[0].$element[0].dataset.dbref,$(this)[0].$element[0].dataset.object,process);},
          updater: function (item) { $("#"+autocompleteelt).val(objList[item]);return item;},
         minLength: 3 
        });
   
   });

   $('.mf-btn').click(function(event) {
    // Submit or clear form
     if(event.target.id.indexOf("mf-save") == 0) {
       mfsubmit("${prefix}");
     }
     if(event.target.id.indexOf("mf-clear") == 0) {
       clear_form_elements("#show-"+curObject);
     }
     if(event.target.id.indexOf("mf-delete") == 0) {
       mfdelete("${prefix}");
       clear_form_elements("#show-"+curObject);
     }
     if(event.target.id.indexOf("mf-search") == 0) {
       mfsearch("${prefix}");
     }
     if(event.target.id.indexOf("mf-search-clear") == 0) {
       clear_form_elements("#mf-search-form-"+curObject);
     }
   });

   $(".mf-form").submit(function(event) {
     return false;
   });

});
</script>
