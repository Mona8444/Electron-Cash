import sys
import time

try:
    from .uikit_bindings import *
except Exception as e:
    sys.exit("Error: Could not import iOS libs: %s"%str(e))


singleton = None

# This class implements a callback "tick" function invoked by the objective c
# CFRunLoop for this app.  This is necessary so the Python interpreter ends up executing
# its threads. Otherwise control exits the interpreter and never returns to it.
# It's a horrible hack but I can't otherwise figure out how to give the jsonrpc server
# timeslices and/or a chance to run.  If you can figure it out, let me know!
# -Calin
class HeartBeat(NSObject):

    @objc_method
    def tick_(self, t):
        if not NSThread.isMainThread:
            print("WARNING: HeartBeat Timer Tick is not in the process's main thread! FIXME!")
        time.sleep(0.020) # give other python "threads" a chance to run..
        try:
            funcs = self.funcs
            en = self.funcs.objectEnumerator()
            inv = en.nextObject()
            while inv:
                inv.invoke()
                inv = en.nextObject()
        except:
            pass


    @objc_method
    def addCallback(self, target, selNameStr):
        try:
            ftest = self.funcs
        except:
            self.funcs = NSMutableArray.alloc().init()
        inv = NSInvocation.invocationWithMethodSignature_(NSMethodSignature.signatureWithObjCTypes_(b'v@:'))
        inv.target = target
        inv.selector = SEL(selNameStr)
        self.funcs.addObject(inv)

    @objc_method
    def start(self):
        self.tickTimer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(0.001, self, SEL(b'tick:'), "tickTimer", True)

    @objc_method
    def stop(self):
        ttest = None
        try:
            ttest = self.tickTimer
        except:
            pass
        if ttest is not None:
            self.tickTimer.invalidate()
            self.tickTimer = None
            
            
def Start():
    global singleton
    if singleton is None:
        singleton = HeartBeat.alloc().init()
        singleton.start()

def Stop():
    global singleton
    if singleton is not None:
        singleton.stop()
        singleton = None
        
def Add(target, selNameStr):
    if singleton is None:
        Start()
    singleton.addCallback(target, selNameStr)
