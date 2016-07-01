from libcpp.vector cimport vector
from libcpp cimport bool
cimport cppsystem
cimport cythonsystem
cimport simulatablesystem
import json
import importlib
import collections

cdef extern from "CppSimulation.hpp":
    cdef cppclass Simulation:
        void simulate(double endtime, double dt, char* solvername,double abs_err, double rel_err, bool dense_output) except +
        void addSystem(simulatablesystem.SimulatableSystem* system)
        double getCurrentTime()

class Runge_Kutta_4:
    """A Runge Kutta 4 solver  that can be used when calculating
     a simulation"""

    name = "rk4"
    def __cinit__(self):
        pass

class Cash_Karp:
    """An adaptive steplength solver that can be used when calculating
     a simulation"""

    name = "ck54"

    def __init__(self):
        self.absolute_error = 1e-10
        self.relative_error = 1e-4

class Dormand_Prince_5:
    """An adaptive steplength solver that can be used when calculating
     a simulation"""

    name = "dp5"

    def __init__(self):
        self.absolute_error = 1e-10
        self.relative_error = 1e-4
        self.dense_output = True

cdef class Sim:
    """This class represents an entire simulation. 
       Each simulation consists of one or more Systems that can be added
       to this class"""
    cdef Simulation * _c_sim
    cdef readonly object systems_list
    cdef readonly object systems

    def __cinit__(self):
        self.systems_list = []
        self.systems = collections.OrderedDict()
        self._c_sim = new Simulation()

    def __dealloc__(self):
        del self._c_sim

    def add_system(self,sys, name = None):
        """Add a system that will participate in this simulation"""
        cdef cppsystem.Sys s
        s = <cppsystem.Sys> (sys)

        #If no name is given give the system instance a name as per:
        #classname, classname_2, classname_3, etc.
        if name is None:
            classname = type(sys).__name__.lower()
            if not (classname in self.systems):
                name = classname
            else:
                for i in range(2,1000):
                    newname = "{}_{}".format(classname,i)
                    if not (newname in self.systems):
                        name = newname
                        break

        cdef simulatablesystem.SimulatableSystem* simsysp
        simsysp = <simulatablesystem.SimulatableSystem*> (s._c_sys)
        self._c_sim.addSystem(simsysp)
        self.systems[name] = sys

    def add_cython_system(self,sys, name):
        cdef cythonsystem.Sys s
        s = <cythonsystem.Sys> (sys)
        cdef simulatablesystem.SimulatableSystem* simsysp
        simsysp = <simulatablesystem.SimulatableSystem*> (s._c_sys)
        self._c_sim.addSystem(simsysp)
        self.systems[name] = sys

    def get_time(self):
        """Get the current time of the simulation.
        Before any simulation has been run this is 0, but after each
        simulation run it is increased
        """
        currentTime = self._c_sim.getCurrentTime()
        return currentTime

    def save_config(self,filepath):
        """Stores the simulations systems and their input values to a file.
        The path for the file to be stored at is given by the arguement'
        "filepath". This file can later be read with the function "load_config".
        """
        systems_dict = collections.OrderedDict()
        for name,system in self.systems.items():
            systemdict = collections.OrderedDict()
            systemdict["type"] = type(system).__name__
            systemdict["module"] = type(system).__module__

            inputdict = collections.OrderedDict()
            for input_name in dir(system.inputs):
                inputdict[input_name] = getattr(system.inputs,input_name)
            systemdict["inputs"]=inputdict

            systems_dict[name]=systemdict

        root_dict = {"systems":systems_dict}

        with open(filepath,'w') as f:
            json.dump(root_dict,
                      f,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))

    def load_config(self,filepath):
        """Loads a number of systems and their input values from a file.
        The file is loaded from the path supplied as an argument to the 
        function
        """
        d = collections.OrderedDict()
        with open(filepath,'r') as f:
            d = json.load(f,object_pairs_hook=collections.OrderedDict)
        systems = d["systems"]
        for name,sys_dict in systems.items():
            modulename = sys_dict["module"]
            typename = sys_dict["type"]
            mod = importlib.import_module(modulename)
            system = getattr(mod,typename)()
            self.add_system(system,name)

            for iname,ivalue in systems[name]["inputs"].items():
                setattr(system.inputs,iname,ivalue)

    def simulate(self, double duration, double dt, solver = Runge_Kutta_4() ):
        """Start or continue a simulation for duration seconds.
        The default ODE-solver used is the classic fixed steplength
        Runge Kutta 4 (rk4), but it is also possible to use other solvers by
        supplying the solver in the argument "solver".
        For fixed lenght algorithms the default time step is 0.1 seconds.
        """
        name  = bytes(solver.name,'utf-8')
        abs_err = 0
        rel_err = 0
        dense = False
        if isinstance(solver, Cash_Karp) or isinstance(solver,Dormand_Prince_5):
            abs_err = solver.absolute_error
            rel_err = solver.relative_error
        if isinstance(solver,Dormand_Prince_5):
            dense = solver.dense_output

        self._c_sim.simulate(duration, dt, name,abs_err,rel_err,dense)