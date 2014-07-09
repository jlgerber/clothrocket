"""
  And EventSubject is a base class for objects which need to be able to fire events. 
  The EventSubject exposes an interface for registering event listeners, and firing events.
"""

#
# Copyright 2010-2012 Fabric Technologies Inc. All rights reserved.
#

import types, copy

import FabricEngine.SceneGraph

class EventSubject(object):
  """A base class providing an inteface for registering event listener callbacks and firing events."""

  __ignoreAllEvents = False
  __eventLoggerCb = None
  __logEventsFor = set() 
  __globalEventListeners = {}

  def __init__(self):
    """Constructor"""
    self.__eventListeners = {}

  @staticmethod
  def enableAllEvents():
    EventSubject.__ignoreAllEvents = False

  @staticmethod
  def disableAllEvents():
    EventSubject.__ignoreAllEvents = True
  
  @classmethod
  def addEventLoggerCb(cls, loggerCb):
    EventSubject.__eventLoggerCb = loggerCb

  @classmethod
  def logEventsFor(cls,event):
    if isinstance(event,(str, unicode)):
      EventSubject.__logEventsFor.append(event)
    elif isinstance(event, (tuple, list, set)):
      EventSubject.__logEventsFor.update(event)

  def addEventListener(self, event, func):
    """Adds a function to the listening stack for a given event name."""
    if event not in self.__eventListeners:
      self.__eventListeners[event] = []
    for listener in self.__eventListeners[event]:
      if listener == func:
        raise FabricEngine.SceneGraph.SceneGraphException("EventListener '"+func.__name__+"' already registered.")
    self.__eventListeners[event].append( func )

  @staticmethod
  def addGlobalEventListener( event, func):
    if event not in EventSubject.__globalEventListeners:
      EventSubject.__globalEventListeners[event] = [func] # should i make this a set?
    else:
      # todo: test to see if func exists for event
      if func in EventSubject.__globalEventListeners[event]:
        raise FabricEngine.SceneGraph.SceneGraphException("EventListener '"+func.__name__+"' already registered.")
      EventSubject.__globalEventListeners[event].append(func)

  def hasEventListener(self, event, func, globalEvents=False):
    """Returns True if this subject has event listeners for a given event name"""
    listeners = self.__eventListeners if globalEvents is False else EventSubject.__globalEventListeners
    if event not in listeners:
      return False
    if func not in listeners[event]:
      return False
    return True
    
  def hasEventListeners(self, event,globalEvents=False):
    """Returns True if this subject has event listeners for a given event name"""
    listeners = self.__eventListeners if globalEvents is False else EventSubject.__globalEventListeners

    if event not in listeners:
      return False
    return len(listeners[event]) > 0
    
  def removeEventListener(self, event, func, globalEvents=False):
    """Removes a function from the listening stack for a given event (string)."""
    glisteners = self.__eventListeners if globalEvents is False else EventSubject.__globalEventListeners

    if event not in glisteners:
      raise FabricEngine.SceneGraph.SceneGraphException("EventListener '"+func.__name__+"' not registered as " + event)
    listeners = glisteners[event]
    index = listeners.index(func)
    if index == -1:
      raise FabricEngine.SceneGraph.SceneGraphException("EventListener '"+func.__name__+"' not registered.")
    del listeners[index]

  def clearEventListener(self, event = None, globalEvents=False):
    """Removes all from the listening stack for a given event (string). If the event is not specified, all events all cleared."""
    glisteners = self.__eventListeners if globalEvents is False else EventSubject.__globalEventListeners

    if event is None:
      glisteners = {}
      return
    elif event in glisteners:
      glisteners[event] = []
    else:
      raise FabricEngine.SceneGraph.SceneGraphException("EventListener '"+func.__name__+"' not registered as " + event)
    
  def fireEvent(self, eventName, data):
    """Invokes all functions on a listening stack for a given event(string)."""
    if EventSubject.__ignoreAllEvents:
      return
    if data is None:
      data = {}
   
    data['eventSubject'] = self

    if eventName in self.__eventListeners:
      if EventSubject.__eventLoggerCb:
        if eventName in EventSubject.__logEventsFor:
          EventSubject.__eventLoggerCb(eventName, data)
      # We copy the listeners array because firing these events may cause listeners to be removed,
      # which causes problems as we are iterating over the list. 
      listeners = copy.copy(self.__eventListeners[eventName])
      for listener in listeners:
        listener(data)

    if eventName in EventSubject.__globalEventListeners:
      if EventSubject.__eventLoggerCb:
        if eventName in EventSubject.__logEventsFor:
          EventSubject.__eventLoggerCb("GLOBAL - %s" %eventName, data)
      # We copy the listeners array because firing these events may cause listeners to be removed,
      # which causes problems as we are iterating over the list.
      listeners = copy.copy(EventSubject.__globalEventListeners[eventName])
      for listener in listeners:
        listener(data)
