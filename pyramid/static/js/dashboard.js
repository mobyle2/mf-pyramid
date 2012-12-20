


   var curObject;

  /**
  * Loads an object and shows its form
  */
  function loadObject(id) {
    clear_form_elements("#show-"+curObject);
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

      var keys = new Array();
      $.each(data, function(obj) {
        //tbody += '<tr id="'+data[obj]["_id"]["$oid"]+'" class="mf-list-object '+id+'">';
        $.each(data[obj], function(key, val) {
          if(! jQuery.isPlainObject(val) || val['$date']!=null) {
            if ( $.inArray(key, keys) < 0) {
              keys.push(key)
            }
            //tbody += "<td>"+val+"</td>";
          }
        });
        //tbody += "</tr>";

      });
      // Table header
      $.each(keys, function(key) { thead += "<th>"+keys[key]+"</th>"; });
      // Now for each object get values from key
      $.each(data, function(obj) {
        tbody += '<tr id="'+data[obj]["_id"]["$oid"]+'" class="mf-list-object '+id+'">';
        $.each(keys, function(key) {
           var val = data[obj][keys[key]];
           if(jQuery.isPlainObject(val) && val['$date']!=null) {
             val = new Date(val['$date']);
           }
          tbody += "<td>"+val+"</td>";
        });
        tbody += "</tr>";
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
       $('#'+curObject+parent+'\\['+key+'\\]').val(val);
       if($('#'+curObject+parent+'\\['+key+'\\]').attr('type')=='checkbox')  {
         if(val == 'True' || val == 1) {
           $('#'+curObject+parent+'\\['+key+'\\]').attr('checked', true);
         }
         else {
           $('#'+curObject+parent+'\\['+key+'\\]').attr('checked', true);
         }
       }
     }

     });
   }

  /**
  * Clear the form elements
  */
  function clear_form_elements(ele) {
    $(ele).find(':input').each(function() {
        switch(this.type) {
            case 'password':
            case 'select-multiple':
            case 'select-one':
            case 'text':
            case 'textarea':
                $(this).val('');
                break;
            case 'checkbox':
            case 'radio':
                this.checked = false;
        }
    });
  }


