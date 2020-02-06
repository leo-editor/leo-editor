#@+leo-ver=5-thin
#@+node:ekr.20170428084207.111: * @file ../external/npyscreen/eveventhandler.py
#@+others
#@+node:ekr.20170428084207.112: ** Declarations
import weakref

#@+node:ekr.20170428084207.113: ** class Event
class Event:
    # a basic event class
    #@+others
    #@+node:ekr.20170428084207.114: *3* __init__
    def __init__(self, name, payload=None):
        self.name = name
        self.payload = payload


    #@-others
#@+node:ekr.20170428084207.115: ** class EventHandler
class EventHandler:
    # This partial base class provides the framework to handle events.

    #@+others
    #@+node:ekr.20170428084207.116: *3* initialize_event_handling
    def initialize_event_handling(self):
        self.event_handlers = {}

    #@+node:ekr.20170428084207.117: *3* add_event_hander
    def add_event_hander(self, event_name, handler):
        if not event_name in self.event_handlers:
            self.event_handlers[event_name] = set()
                # weakref.WeakSet() #Why doesn't the WeakSet work?
        self.event_handlers[event_name].add(handler)

        parent_app = self.find_parent_app()
        if parent_app:
            parent_app.register_for_event(self, event_name)
        else:
            # Probably are the parent App!
            # but could be a form outside a proper application environment
            try:
                self.register_for_event(self, event_name)
            except AttributeError:
                pass

    #@+node:ekr.20170428084207.118: *3* remove_event_handler
    def remove_event_handler(self, event_name, handler):
        if event_name in self.event_handlers:
            self.event_handlers[event_name].remove(handler)
        if not self.event_handlers[event_name]:
            self.event_handlers.pop({})


    #@+node:ekr.20170428084207.119: *3* handle_event
    def handle_event(self, event):
        "return True if the event was handled.  Return False if the application should stop sending this event."
        if event.name not in self.event_handlers:
            return False
        else:
            remove_list = []
            for handler in self.event_handlers[event.name]:
                try:
                    handler(event)
                except weakref.ReferenceError:
                    remove_list.append(handler)
            for dead_handler in remove_list:
                self.event_handlers[event.name].remove(handler)
            return True

    #@+node:ekr.20170428084207.120: *3* find_parent_app
    def find_parent_app(self):
        if hasattr(self, "parentApp"):
            return self.parentApp
        elif hasattr(self, "parent") and hasattr(self.parent, "parentApp"):
            return self.parent.parentApp
        else:
            return None

    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
