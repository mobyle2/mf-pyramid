<%inherit file="layout.mako"/>

<ul class="nav nav-tabs">
  <li class="active">
    <a href="#" id="dashboard">Dashboard</a>
  </li>
  % for object in objects:
  <li><a href="#" class="dashboard-item" id="${object}">${object}s</a></li>
  % endfor
</ul>
<div id="mf-flash" class="mf-flash"></div>
% for object in objects:
<div id="list-${object}" class="mf-list">
  <table class="mf-table table table-hover" id="table-${object}">
  </table>
</div>
% endfor

% for object in klasses:
<div id="show-${object.__name__}" class="mf-object offset1">
  ${object().render() | n}
</div>
% endfor

</div>

<script>



   var curObject;

   $(".mf-list").hide();
   $(".mf-object").hide();
   $(".dashboard-item").click(function(event){
     object = event.target.id;
     curObject = object
     loadObjectList(object);
   });

   $(".mf-list-object").live("click", function(event) {
     object = $(event.target).parent().attr("id");
     loadObject(object);
   });

   $('.mf-del').live("click", function(event) {
    obj = $(this).attr('elt');
    arrayelts = $('#'+obj);
    if(arrayelts.size()==1) { alert("Cannot delete this element, list must contain at least one (possibly empty) parameter"); }
    else { $(this).parent().remove();}
   });

   $('.mf-add').click(function(event) {
    obj = $(this).attr('elt');
    arrayelts = $('#'+obj);
    firstelt = $(arrayelts[0]);
    template = firstelt.parent().parent().parent().clone();
    main = firstelt.parent().parent().parent().parent();
    template.find('input').val('');
    main.append(template);
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
   });

   $(".mf-form").submit(function(event) {
     return false;
   });


</script>
