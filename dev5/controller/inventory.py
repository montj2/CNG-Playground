#!/usr/bin/python
################################################################################
# INVENTORY
#
# Justin Dierking
# justin.l.dierking.civ@mail.mil
# (614) 692 2050
#
# 10/16/2016 Original construction
# 03/20/2017 Overhauled import and export methods to include links and 
#              containers. Pre-existing child node references are also
#              preserved now to enable precise bulk imports and exports.
# 04/11/2017 Moved import logic to inventory model.
#            Added zip import and export routes.
#            Renamed json import and export routes.
################################################################################

import cherrypy
import json
import traceback
import zipfile
import StringIO
import hashlib

from cherrypy.lib.static import serve_fileobj
from time import sleep, time

from .messaging import add_message

from .auth import require
from ..model import schedule
from ..model.document import Collection
from ..model.datastore import File as DatastoreFile
from ..model.inventory import get_child_nodes, \
                              get_status_objects, \
                              set_parent_objuuid, \
                              get_context_menu, \
                              delete_node, \
                              create_container, \
                              create_task, \
                              create_link, \
                              create_procedure, \
                              create_controller, \
                              create_rfc, \
                              create_schedule, \
                              create_text_file, \
                              create_binary_file, \
                              create_status_code, \
                              create_host, \
                              create_host_group, \
                              create_console, \
                              get_dependencies, \
                              copy_object, \
                              get_provided_objects_grid, \
                              get_required_objects_grid, \
                              import_objects
from ..model.eventlog import create_inventory_move_event, \
                             create_inventory_copy_event, \
                             create_inventory_create_event, \
                             create_inventory_delete_event, \
                             create_inventory_import_event, \
                             create_inventory_export_event
                              
class Inventory(object):
    def __init__(self):
        self.moving = False

    @cherrypy.expose
    @require()
    def ajax_roots(self, objuuid):
        add_message("inventory controller: load inventory: {0}".format(objuuid))
        try:
            return json.dumps(get_child_nodes(objuuid))
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_move(self, objuuid, parent_objuuid):
        add_message("inventory controller: move inventory object: {0}".format(objuuid))
        while self.moving:
            sleep(.1)
        
        try:
            self.moving = True
            set_parent_objuuid(objuuid, parent_objuuid)
        except Exception as e:
            add_message(traceback.format_exc())
        finally:
            self.moving = False
        
        #create_inventory_move_event(Collection("users").find(sessionid = cherrypy.session.id)[0], \
        #                            Collection("inventory").get_object(objuuid))
        
        return json.dumps({})
    
    @cherrypy.expose
    @require()
    def ajax_copy_object(self, objuuid):
        add_message("inventory controller: copy: {0}".format(objuuid))

        try:
            while self.moving:
                sleep(.1)
            
            return json.dumps(copy_object(objuuid).object)
        except Exception:
            add_message(traceback.format_exc())
        
        #create_inventory_copy_event(Collection("users").find(sessionid = cherrypy.session.id)[0], \
        #                            Collection("inventory").get_object(objuuid))
        
    
    @cherrypy.expose
    @require()
    def ajax_create_container(self, objuuid):
        add_message("inventory controller: create container: {0}".format(objuuid))
        try:
            container = create_container(objuuid, "New Container")
            
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], container)
        
            return json.dumps(container.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_host(self, objuuid):
        add_message("inventory controller: create host: {0}".format(objuuid))
        try:
            host = create_host(objuuid, "New Host")
            
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], host)
        
            return json.dumps(host.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_text_file(self, objuuid):
        add_message("inventory controller: create text_file: {0}".format(objuuid))
        try:
            text_file = create_text_file(objuuid, "New Text File.txt")
            
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], text_file)
        
            return json.dumps(text_file.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_host_group(self, objuuid):
        add_message("inventory controller: create host group: {0}".format(objuuid))
        try:
            group = create_host_group(objuuid, "New Host Group")
            
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], group)
        
            return json.dumps(group.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_console(self, objuuid):
        add_message("inventory controller: create console: {0}".format(objuuid))
        try:
            console = create_console(objuuid, "New Console")
            
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], console)
        
            return json.dumps(console.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_task(self, objuuid):
        add_message("inventory controller: create task: {0}".format(objuuid))
        try:
            current_user = Collection("users").find(sessionid = cherrypy.session.id)[0]
            
            task = create_task(objuuid, \
                               "New Task", \
                               author = "{0} {1}".format(current_user.object["first name"], \
                                                         current_user.object["last name"]), \
                               email = current_user.object["email"], \
                               phone = current_user.object["phone"])
            
            #create_inventory_create_event(current_user, task)
            
            return json.dumps(task.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_schedule(self, objuuid):
        add_message("inventory controller: create schedule: {0}".format(objuuid))
        try:
            schedule = create_schedule(objuuid, "New Schedule")
        
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], schedule)
            
            return json.dumps(schedule.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_status_code(self, objuuid):
        add_message("inventory controller: create status code: {0}".format(objuuid))
        try:
            status_code = create_status_code(objuuid, "New Status Code")
            
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], status_code)
            
            return json.dumps(status_code.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_procedure(self, objuuid):
        add_message("inventory controller: create procedure: {0}".format(objuuid))
        try:
            procedure = create_procedure(objuuid, "New Procedure")
        
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], procedure)
            
            return json.dumps(procedure.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_controller(self, objuuid):
        add_message("inventory controller: create controller: {0}".format(objuuid))
        try:
            controller = create_controller(objuuid, "New Controller")
            
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], controller)
            
            return json.dumps(controller.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_rfc(self, objuuid):
        add_message("inventory controller: create RFC: {0}".format(objuuid))
        try:
            rfc = create_rfc(objuuid, "New RFC")
            
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], rfc)
            
            return json.dumps(rfc.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_link(self, objuuid):
        add_message("inventory controller: create link to {0}".format(objuuid))
        try:
            return json.dumps(create_link(objuuid).object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_delete(self, objuuid):
        add_message("inventory controller: delete inventory object: {0}".format(objuuid))
        try:
            while self.moving:
                sleep(.1)
            
            #create_inventory_delete_event(Collection("users").find(sessionid = cherrypy.session.id)[0], \
            #                              Collection("inventory").get_object(objuuid))
            
            delete_node(objuuid)
            return json.dumps({"id" : objuuid})
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_context(self, objuuid):
        add_message("inventory controller: get context menu: {0}".format(objuuid))
        try:
            return json.dumps(get_context_menu(objuuid))
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_dependencies(self):
        add_message("inventory controller: get dependencies...")
        try:
            cl = cherrypy.request.headers['Content-Length']
            objuuids = json.loads(cherrypy.request.body.read(int(cl)))
            return json.dumps(get_dependencies(objuuids))
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_object(self, objuuid):
        add_message("inventory controller: get inventory object...")
        try:
            collection = Collection("inventory")
            object = collection.get_object(objuuid).object
            add_message("inventory controller: get: {0}, type: {1}, name: {2}".format(objuuid, object["type"], object["name"]))
            return json.dumps(object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_status_objects(self):
        add_message("inventory controller: get status objects...")
        try:
            return json.dumps(get_status_objects())
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_post_object(self):
        add_message("inventory controller: post inventory object...")
        
        try:
            cl = cherrypy.request.headers['Content-Length']
            object = json.loads(cherrypy.request.body.read(int(cl)))
        
            collection = Collection("inventory")
            current = collection.get_object(object["objuuid"])
            current.object = object
            current.set()
            
            add_message("inventory controller: set: {0}, type: {1}, name: {2}".format(object["objuuid"], object["type"], object["name"]))
        
            return json.dumps(current.object)
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def export_objects_json(self, objuuids):
        add_message("inventory controller: exporting inventory objects...")
        
        try:
            collection = Collection("inventory")
        
            inventory = {}
            
            for objuuid in objuuids.split(","):
                current = collection.get_object(objuuid)
                
                if current.object["type"] != "binary file":
                    inventory[objuuid] = current.object
                    add_message("inventory controller: exported: {0}, type: {1}, name: {2}".format(objuuid, current.object["type"], current.object["name"]))
        
            cherrypy.response.headers['Content-Type'] = "application/x-download"
            cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=export.{0}.json'.format(time())
            
            #create_inventory_export_event(Collection("users").find(sessionid = cherrypy.session.id)[0], objuuids.split(","))
            
            add_message("INVENTORY EXPORT COMPLETE")
            
            return serve_fileobj(json.dumps(inventory))
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def export_objects_zip(self, objuuids):
        add_message("inventory controller: exporting inventory objects...")
        
        try:
            collection = Collection("inventory")
        
            inventory = {}
            
            dstuuids = []
            
            for objuuid in objuuids.split(","):
                current = collection.get_object(objuuid)
                inventory[objuuid] = current.object
                
                if current.object["type"] == "binary file":
                    dstuuids.append(current.object["sequuid"])
                
                add_message("inventory controller: exported: {0}, type: {1}, name: {2}".format(objuuid, current.object["type"], current.object["name"]))
                
            cherrypy.response.headers['Content-Type'] = "application/x-download"
            cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=export.{0}.zip'.format(time())
            
            mem_file = StringIO.StringIO()
            
            with zipfile.ZipFile(mem_file, mode = 'w', compression = zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('inventory.json', json.dumps(inventory))
                
                for dstuuid in dstuuids:
                    zf.writestr('{0}.bin'.format(dstuuid), buffer(DatastoreFile(dstuuid).read()))
            
            #create_inventory_export_event(Collection("users").find(sessionid = cherrypy.session.id)[0], objuuids.split(","))
            
            add_message("INVENTORY EXPORT COMPLETE")
            
            return serve_fileobj(mem_file.getvalue())
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_required_objects_grid(self, objuuid):
        add_message("inventory controller: get required objects grid: {0}".format(objuuid))
        try:
            return json.dumps(get_required_objects_grid(objuuid))
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_provided_objects_grid(self, objuuid):
        add_message("inventory controller: get provided objects grid: {0}".format(objuuid))
        try:
            return json.dumps(get_provided_objects_grid(objuuid))
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def import_objects_json(self, file):
        add_message("inventory controller: importing inventory objects...")
        
        try:
            objects = json.loads(file.file.read())
        
            import_objects(objects)
            
            objuuids = []
            for objuuid in objects:
                objuuids.append(objuuid)
            
            #create_inventory_import_event(Collection("users").find(sessionid = cherrypy.session.id)[0], objuuids)
        except Exception:
            add_message(traceback.format_exc())
        
        add_message("INVENTORY IMPORT COMPLETE")
        
        return json.dumps({})
    
    @cherrypy.expose
    @require()
    def import_objects_zip(self, file):
        add_message("inventory controller: importing inventory objects...")
        
        try:
            archive = zipfile.ZipFile(file.file, 'r')
            
            objects = json.loads(archive.read("inventory.json"))
            
            for objuuid, object in objects.iteritems():
                if object["type"] == "binary file":
                    datastore_file = DatastoreFile(object["sequuid"])
                    
                    zipped_file = archive.open("{0}.bin".format(object["sequuid"]), "r")
                    
                    sha1hash = hashlib.sha1()
                    
                    for chunk in iter(lambda: zipped_file.read(65536), b''):
                        datastore_file.write(chunk)
                        sha1hash.update(chunk)
                    
                    datastore_file.truncate()
                    
                    object["size"] = datastore_file.size()
                    object["sha1sum"] = sha1hash.hexdigest()
            
            import_objects(objects)
            
            objuuids = []
            for objuuid in objects:
                objuuids.append(objuuid)
            
            #create_inventory_import_event(Collection("users").find(sessionid = cherrypy.session.id)[0], objuuids)
        except Exception:
            add_message(traceback.format_exc())
        
        add_message("INVENTORY IMPORT COMPLETE")
        
        return json.dumps({})
    
    @cherrypy.expose
    @require()
    def import_text_file(self, file):
        add_message("inventory controller: importing text file...")
        
        try:
            text_file = create_text_file("#", file.filename)
            text_file.object["body"] = file.file.read()
            text_file.set()
            
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], text_file)
            
        except Exception:
            add_message(traceback.format_exc())
        
        add_message("INVENTORY IMPORT COMPLETE")
        
        return json.dumps({})
    
    @cherrypy.expose
    @require()
    def import_binary_file(self, file):
        add_message("inventory controller: importing binary file...")
        
        try:
            binary_file_inv = create_binary_file("#", file.filename)
            
            binary_file_dst = DatastoreFile(binary_file_inv.object["sequuid"])
            
            sha1hash = hashlib.sha1()
            
            for chunk in iter(lambda: file.file.read(65536), b''):
                binary_file_dst.write(chunk)
                sha1hash.update(chunk)
            
            binary_file_inv.object["size"] = binary_file_dst.size()
            binary_file_inv.object["sha1sum"] = sha1hash.hexdigest()
            binary_file_inv.set()
            
            #create_inventory_create_event(Collection("users").find(sessionid = cherrypy.session.id)[0], binary_file_inv)
        except Exception:
            add_message(traceback.format_exc())
        
        add_message("INVENTORY IMPORT COMPLETE")
        
        return json.dumps({})