import avahi
import dbus
import gobject
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop

__all__ = ["ZeroconfService", "ZeroconfClient"]


class ZeroconfService:
    """
    Publishes a Zeroconf Service
    http://stackp.online.fr/?p=35
    http://stackoverflow.com/questions/3430245/how-to-develop-an-avahi-client-server
    """

    def __init__(self, name, port, stype="_http._tcp",
                 domain="", host="", text=""):
        self.name = name
        self.stype = stype
        self.domain = domain
        self.host = host
        self.port = port
        self.text = text

    def publish(self):
        bus = dbus.SystemBus()
        server = dbus.Interface(
                        bus.get_object(
                                avahi.DBUS_NAME,
                                avahi.DBUS_PATH_SERVER),
                        avahi.DBUS_INTERFACE_SERVER)

        g = dbus.Interface(
                    bus.get_object(avahi.DBUS_NAME,
                                   server.EntryGroupNew()),
                    avahi.DBUS_INTERFACE_ENTRY_GROUP)

        g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                     self.name, self.stype, self.domain, self.host,
                     dbus.UInt16(self.port), self.text)

        g.Commit()
        self.group = g

    def unpublish(self):
        self.group.Reset()


class ZeroconfClient:
    """
    Discovers and resolves Zeroconf Services
    http://avahi.org/wiki/PythonBrowseExample
    """

    def __init__(self, stype="_http._tcp",
                 reply_handler=None,
                 error_handler=None,
                 ignore_local=True):
        if reply_handler:
            self.reply_handler = reply_handler
        else:
            self.reply_handler = self._service_resolved
        if error_handler:
            self.error_handler = error_handler
        else:
            self.error_handler = self._service_resolve_failed

        self.ignore_local = ignore_local

        loop = DBusGMainLoop()
        self.bus = dbus.SystemBus(mainloop=loop)
        self.server = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, '/'),
                'org.freedesktop.Avahi.Server')

        sbrowser = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME,
                self.server.ServiceBrowserNew(avahi.IF_UNSPEC,
                    avahi.PROTO_UNSPEC, stype, 'local', dbus.UInt32(0))),
                avahi.DBUS_INTERFACE_SERVICE_BROWSER)
        sbrowser.connect_to_signal("ItemNew", self.resolve_handler)

        gobject.MainLoop().run()

    def stop(self):
        gobject.MainLoop().stop()

    def _service_resolved(*args):
        print 'service resolved'
        print 'name:', args[2]
        print 'address:', args[7]
        print 'port:', args[8]

    def _service_resolve_failed(*args):
        print 'error_handler'
        print args[0]

    def resolve_handler(self, interface, protocol, name, stype, domain, flags):
        if flags & avahi.LOOKUP_RESULT_LOCAL:
            # local service, skip
            pass

        self.server.ResolveService(interface, protocol, name, stype,
            domain, avahi.PROTO_UNSPEC, dbus.UInt32(0),
            reply_handler=self.reply_handler,
            error_handler=self.error_handler)
