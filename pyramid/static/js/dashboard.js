


   var curObject;

  /**
  * Loads an object and shows its form
  */
  function loadObject(id) {
    route = '/'+curObject.toLowerCase()+'s/'+id;
    $.getJSON(route, function(data) {
      $("#show-"+curObject).show();
      json2form(data["user"],"");
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


   /**
   * Map a json result to a form
   */
   function json2form(data,parent) {
     $.each(data, function(key, val) {
     if(jQuery.isPlainObject(val)) {
       if(val['$date']!=null){
         var objdate = new Date(val['$date']);
         var objdatestr = objdate.toString()
         var type = $('#'+curObject+parent+'\\['+key+'\\]').attr('type');
         if (type == 'date') { objdatestr = objdate.toDateString(); }
         if (type == 'time') { objdatestr = objdate.toTimeString(); }
         $('#'+curObject+parent+'\\['+key+'\\]').val(objdatestr);
       }
       else if(val['$oid']!=null){
         $('#'+curObject+parent+'\\['+key+'\\]').val(val['$oid']);
       }
       else {
         var newparent = parent + '\\['+key+'\\]';
         json2form(val,newparent);
       }
     }
     else { 
       console.log("update "+key+" search "+'#'+curObject+parent+'\\['+key+'\\]'+" with val "+val);
       $('#'+curObject+parent+'\\['+key+'\\]').val(val);
     }

     });
   }

