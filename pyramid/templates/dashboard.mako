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

    obj = obj.replace('[','\\[');
    obj = obj.replace(']','\\]');
    arrayelts = $('#Template'+obj);
    template = $(arrayelts[0]).children();
          
    clonediv = $('#Clone'+obj);
    newelt = template.clone();
    newelt.find('input').val('');
    clonediv.append(newelt);


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
   });

   $(".mf-form").submit(function(event) {
     return false;
   });


</script>
