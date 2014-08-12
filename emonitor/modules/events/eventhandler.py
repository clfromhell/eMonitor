from emonitor.extensions import db, events


class Eventhandler(db.Model):
    __tablename__ = 'eventhandlers'

    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(32))
    handler = db.Column(db.String(64))
    position = db.Column(db.Integer, default=0)
    parameters = db.Column(db.Text, default="")

    def __init__(self, event, handler, position, parameters):
        self.event = event
        self.handler = handler
        self.position = position
        self.parameters = parameters
        
    def getParameterValue(self, parameter):
        for p in self.parameters.split("\r\n"):
            if p.startswith(parameter + "="):
                return p.split('=')[-1]
        return ""
        
    def getParameterList(self, t='out'):
        return [param.split('=')[0] for param in self.parameters.split('\r\n') if param.startswith(t + '.')]
        
    def getParameterValues(self, t='out'):
        return [param.split('=') for param in self.parameters.split('\r\n') if param.startswith(t + '.')]
        
    def getInParameters(self):
        event = events.getEvents(self.event)
        if self.position < 2:
            return event.parameters
        elif self.position == '':
            if len(event.getHandlers()) > 0:
                hdl = event.getHandlers()[-1]
                return hdl.getParameterList() + event.parameters  # add event parameters
            else:
                return []
        else:
            for hdl in event.getHandlers():
                if hdl.position == self.position - 1:
                    #return [param.split('=')[0] for param in hdl.parameters.split('\r\n') if param.startswith('out.')]
                    return hdl.getParameterList() + event.parameters  # add event parameters

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id, 'event': self.event, 'handler': self.handler, 'position': self.position, 'parameters': self.parameters}

    @staticmethod
    def getEventhandlers(id="", event=""):
        if id != '':
            return db.session.query(Eventhandler).filter_by(id=id).first()
        elif event != '':
            return db.session.query(Eventhandler).filter_by(event=event).order_by('position').all()
        else:
            return db.session.query(Eventhandler).order_by('event', 'position').all()
