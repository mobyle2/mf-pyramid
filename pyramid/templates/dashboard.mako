<%inherit file="layout.mako"/>

<ul class="nav nav-tabs">
  <li class="active">
    <a href="#" id="dashboard">Dashboard</a>
  </li>
  % for object in objects:
  <li><a href="#" class="dashboard-item" id="${object}">${object}s</a></li>
  % endfor
</ul>

% for object in objects:
<div id="list-${object}" class="mf-list">
  <table class="mf-table table table-hover" id="table-${object}">
  </table>
</div>
% endfor

% for object in klasses:
<div id="show-${object.__name__}" class="mf-object">
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


</script>
