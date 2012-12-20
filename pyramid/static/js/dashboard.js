


   var curObject;

  /**
  * Loads an object and shows its form
  */
  function loadObject(id) {
    route = '/'+curObject.toLowerCase()+'s/'+id;
    $.getJSON(route, function(data) {
      $("#show").html("<p>"+data["user"]["name"]+"</p>");
      $("#show").show();
     });
  }

  /**
  * Loads a list of objects and create a sortable table
  */
  function loadObjectList(id) {
    
    $(".mf-list").hide();
    $(".mf-object").hide();
    route = '/'+id.toLowerCase()+'s/';
    $.getJSON(route, function(data) {
      var thead = '<thead><tr>';
      var tbody = '<tr>';
      var first = 1;
      $.each(data, function(obj) {
        tbody += '<tr id="'+data[obj]["_id"]["$oid"]+'" class="mf-list-object '+id+'">';
        $.each(data[obj], function(key, val) {
          if(! jQuery.isPlainObject(val)) {
            if(first == 1) { thead += "<th>"+key+"</th>"; }
            tbody += "<td>"+val+"</td>";
          }
        });
        tbody += "</tr>";
        first = 0;
      });
      thead += '</tr></thead>';
      tbody += '</tbody>';
      $("#table-"+id).html(thead+tbody);
      $("#list-"+id).show();
     });
   }

