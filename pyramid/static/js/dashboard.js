
/**
* Javascritp library used in example dashboard
*
*
**/

   var curObject;

  /**
  * Delete an object
  */
  function mfdelete(prefix){
    id = $("#"+curObject+"\\[_id\\]").val();
    route = '/'+curObject.toLowerCase()+'s/'+id;
     $.ajax({type:"DELETE", url: route,
            success: function(msg){
              if(msg["status"]==1) {
                $("#mf-flash").attr('class','alert alert-error');
                $("#mf-flash").text(curObject+" could not be deleted");
              }
              else {
                $("#mf-flash").attr('class','alert alert-success');
                $("#mf-flash").text(curObject+" deleted");
                loadObjectList(curObject);
              }               
            },
            error: function(){
                alert('An error occured during transaction');
            }
        });

  }

  /**
  * Set checkboxes values to True or False according to checked status.
  * Not very performant for the moment as it resets all checkboxes values.
  */
  function updateCheckboxValues() {
     checks = $('input[type=checkbox]').not(':checked');
     $.each(checks,function() {
       $(this).val('False');
     });
     checks = $('input:checked');
     $.each(checks,function() {
       $(this).val('True');
     });
  }

  /**
  * Search
  */
  function mfsearch(prefix) {
     updateCheckboxValues();
     $.ajax({type:"POST", data: $("#mf-search-form-"+curObject).serialize(), url: prefix+"/"+curObject.toLowerCase()+"s/",
            success: function(msg){
               if(msg["status"]==1) {
                   $("#mf-flash").attr('class','alert alert-error');
                   $("#mf-flash").text("An error occured with the search");
               }
               else {
                   $("#mf-flash").attr('class','alert alert-success');
                   updateObjectList(msg);
               }
            },
            error: function(){
                alert('An error occured during transaction');
            }
        });

  }

  /**
  * Submit the form
  */
  function mfsubmit(prefix) {
     updateCheckboxValues();
     id = $("#"+curObject+"\\[_id\\]").val();
     method = "POST";
     if(id ==null || id == '') { method = "PUT"; id = "" }
     $.ajax({type:method, data: $("#mf-form-"+curObject).serialize(), url: prefix+"/"+curObject.toLowerCase()+"s/"+id,
            success: function(msg){
               if(msg["status"]==1) {
                 $.each(msg["error"], function(err){
                     params = msg["error"][err].split('.');
                     errparam = '';
                     for(var i=0;i<params.length;i++) {
                       errparam += '\\['+params[i]+'\\]'
                     }
                     $("#"+curObject+errparam).attr('class','mf-error');
                  });

                 $("#mf-flash").attr('class','alert alert-error');
                 $("#mf-flash").text(curObject+" could not be saved");
               }
               else {
                 clear_form_elements("#show-"+curObject);
                 $("#mf-flash").attr('class','alert alert-success');
                 if(method == "POST") {
                   $("#mf-flash").text(curObject+" successfully updated");
                 }
                 else { 
                   $("#mf-flash").text(curObject+" successfully added");
                 }
               }
               loadObjectList(curObject,false);
            },
            error: function(){
                alert('An error occured during transaction');
            }
        });
   }


  /**
  * Loads an object and shows its form
  */
  function loadObject(id) {
    clear_form_elements("#show-"+curObject);
    route = '/'+curObject.toLowerCase()+'s/'+id;
    $.getJSON(route, function(data) {
      json2form(data[curObject.toLowerCase()],"");
     });
  }

  function loadObjectList(id) {
    loadObjectList(id,true);
  }

  /**
  * Loads a list of objects and create a sortable table
  */
  function loadObjectList(id,clean) {
    if(clean) {
      clear_form_elements("#show-"+curObject);
    }
    $(".mf-list").hide();
    //$(".mf-object").hide();
    $(".accordion").hide();
    //$(".mf-search").hide();
    $("#accordion"+curObject).show();
    //$("#show-"+curObject).show();
    //$("#search-"+curObject).show();
    route = '/'+id.toLowerCase()+'s/';
    $.getJSON(route, function(data) {
     updateObjectList(data);
     });
   }


   /**
   * Update list of object from json list
   */
   function updateObjectList(data) {
      var thead = '<thead><tr>';
      var tbody = '<tr>';

      var keys = new Array();
      var types = {};
      $.each(data, function(obj) {
        $.each(data[obj], function(key, val) {
          if( key!='id' && val!=null && ((!jQuery.isPlainObject(val)) || val['$date']!=null )) {
            var type = $('#'+curObject+'\\['+key+'\\]').attr('type');
            if ( $.inArray(key, keys) < 0) {
              keys.push(key)
              types[key] = type
            }
          }
        });

      });
      // Table header
      $.each(keys, function(key) { thead += "<th>"+keys[key]+"</th>"; });
      // Now for each object get values from key
      $.each(data, function(obj) {
        tbody += '<tr id="'+data[obj]["_id"]["$oid"]+'" class="mf-list-object '+curObject+'">';
        $.each(keys, function(key) {
           var val = data[obj][keys[key]];
           // Bson does not permit python time or date conversion, so we store them as string.
           if((jQuery.isPlainObject(val) && val['$date']!=null) || (types[keys[key]] == 'date') || (types[keys[key]] == 'time')) {          
             if (types[keys[key]] == 'date') {
               //val = dateFormat(val,'yyyy/mm/dd');
             }
             else if (types[keys[key]] == 'time') {
               //val = dateFormat(val,'hh:MM:ss');
             }
             else {
               val = new Date(val['$date']);
               val = dateFormat(val,'yyyy/mm/dd hh:MM:ss');
             }
           }
          tbody += "<td>"+val+"</td>";
        });
        tbody += "</tr>";
      });

      thead += '</tr></thead>';
      tbody += '</tbody>';
      $("#table-"+curObject).html(thead+tbody);
      $("#list-"+curObject).show();
   }


   /**
   * Map a json result to a form
   */
   function json2form(data,parent) {
     $.each(data, function(key, val) {
     if(jQuery.isPlainObject(val)) {
       if(val['$date']!=null){
         var objdate = new Date(val['$date']);
         //var objdatestr = objdate.toString()
         var month = objdate.getMonth()+1;
         if (month<10) { month = '0'+month; }
         var day = objdate.getDate();
         if (day<10) { day = '0'+day; }
         var hours = objdate.getHours();
         if (hours<10) { hours = '0'+hours; }
         var minutes = objdate.getMinutes();
         if (minutes<10) { minutes = '0'+minutes; }
         var seconds = objdate.getSeconds();
         if (seconds<10) { seconds = '0'+seconds; }
         var objdatestr = objdate.getFullYear()+'/'+month+'/'+day+' '+hours+':'+minutes+':'+seconds
         var type = $('#'+curObject+parent+'\\['+key+'\\]').attr('type');
         if (type == 'date') { objdatestr = objdate.toDateString(); }
         if (type == 'time') { objdatestr = objdate.toTimeString(); }
         $('#'+curObject+parent+'\\['+key+'\\]').val(objdatestr);
       }
       else if(val['$oid']!=null){
         $('#'+curObject+parent+'\\['+key+'\\]').val(val['$oid']);
       }
       else if(val['_id']!=null && val['_id']['$oid']!=null){
         // Db object reference
         $('#'+curObject+parent+'\\['+key+'\\]').val(val['_id']['$oid']);
         $('#DbRef'+curObject+parent+'\\['+key+'\\]').text(val['_id']['$oid']);
         searchDbRef(curObject+parent+'\\['+key+'\\]');
       }       
       else {
         var newparent = parent + '\\['+key+'\\]';
         json2form(val,newparent);
       }
     }
     else {
       if(val instanceof Array) {
           arrayelts = $('#Template'+curObject+parent+'\\['+key+'\\]');
           template = $(arrayelts[0]).children();
          
           clonediv = $('#Clone'+curObject+parent+'\\['+key+'\\]');
           clonediv.children().remove();

           $.each(val, function(elt) {
             newelt = template.clone(true,true);
             
            inputs = newelt.find('input:not(.mf-dbref)');
            $.each(inputs, function(input) {
              ielt = $(inputs[input])
              oldid = ielt.attr("id");
              ielt.attr("id",oldid+count);
              ielt.attr("name",oldid+count);
              if(jQuery.isPlainObject(val[elt])) {
                 $.each(val[elt], function(key,value) {
                   reg1=new RegExp(key,"g");
                   if(oldid.match(reg1)) {
                     ielt.val(val[elt][key]);
                   }
                 });
              }
              else {
                ielt.val(val[elt]);
              }
              newdbref = newelt.find("#DbRef"+dbrefobj);
              newdbref.attr("data-dbref",oldid+count);
        	  newdbref.attr("id",oldid+count);
              //$('#DbRef'+oldid).attr("data-dbref",oldid+count);
              //$('#DbRef'+oldid).attr("id",oldid+count);
            });
             
             
             //oldid = newelt.find('input:not(.mf-dbref)').attr("id");
             //newelt.find('input:not(.mf-dbref)').attr("id",oldid+count);
             //newelt.find('.mf-dbref').attr("data-dbref",oldid+count);          
             //newelt.find('input:not(.mf-dbref)').val(val[elt]);
             clonediv.append(newelt);
             searchDbRef(oldid+count);
             count++;
           });

       }
       else {
         $('#'+curObject+parent+'\\['+key+'\\]').val(val);
         if($('#'+curObject+parent+'\\['+key+'\\]').attr('type')=='checkbox')  {
           if(val == 'true' || val == 'True' || val == 1) {
             $('#'+curObject+parent+'\\['+key+'\\]').attr('checked', true);
           }
           else {
             $('#'+curObject+parent+'\\['+key+'\\]').attr('checked', false);
           }
         }
       }
     }

     });
   }

  /**
  * Search the name of an object from its id and update object container.
  * get id, search in database and update name in dbref container.
  */
  function searchDbRef(container){

      id = $('#'+container).val();
      var obj = $('#DbRef'+container).attr("data-object");
      if(obj==null) { return; }
      route = '/'+obj.toLowerCase()+'s/'+id;
      $.getJSON(route, function(data) {
        if(data[obj.toLowerCase()]['name']!=null) {
          $('#DbRef'+container).val(data[obj.toLowerCase()]['name']);
        }
      });
  }


  /**
  * Clear the form elements
  */
  function clear_form_elements(ele) {
    $(".mf-template-clone").children().remove();
    $("div").removeClass("error");
    $("#mf-flash").attr('class','');
    $("#mf-flash").text("");
    $(ele).find(':input').each(function() {
        switch(this.type) {
            case 'password':
            case 'select-multiple':
            case 'select-one':
            case 'text':
            case 'textarea':
            case 'hidden':
                $(this).attr('class','');
                $(this).val('');
                break;
            case 'checkbox':
            case 'radio':
                this.checked = false;
        }
    });
  }

  /**
  * Clear the search form elements
  */
  function clear_search_form_elements(ele) {
    $(ele).find(':input').each(function() {
        switch(this.type) {
            case 'password':
            case 'select-multiple':
            case 'select-one':
            case 'text':
            case 'textarea':
                $(this).attr('class','');
                $(this).val('');
                break;
            case 'checkbox':
            case 'radio':
                this.checked = false;
        }
    });
  }

  /**
  * Get object list and set objList with obj name/obj id
  */
  function getObjects(query,param,objname,process) {
    autocompleteelt = param;
    autocompleteelt = autocompleteelt.replace('[','\\[');
    autocompleteelt = autocompleteelt.replace(']','\\]');
    route = '/'+objname.toLowerCase()+'s/';
    return $.ajax({type:"POST", data: 'Search'+objname+"[name]="+query, url: route,
            success: function(msg){
               if(msg["status"]==1) {
                   $("#mf-flash").attr('class','alert alert-error');
                   $("#mf-flash").text("An error occured with the search");
               }
               else {
                   $("#mf-flash").attr('class','alert alert-success');
                   objList = {};
                   nameList = [];
                   $.each(msg, function(obj) {
                     objList[msg[obj]["name"]] = msg[obj]["_id"]["$oid"];
                     nameList.push(msg[obj]["name"]);
                   });
               return process(nameList);
               }
            },
            error: function(){
                alert('An error occured during transaction');
            }
     });


  }


