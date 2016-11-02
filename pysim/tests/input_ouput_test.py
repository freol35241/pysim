"""This module contains tests for the setting and reading of inputs and outputs
"""
import re

import pytest
import numpy as np

from pysim.simulation import Sim

import pysim.cythonsystem

from pysim.systems import Adder3D
from pysim.systems import Adder
from pysim.systems import VanDerPol
from pysim.systems import MassSpringDamper
from pysim.systems import ReadTextInput
from pysim.systems import InOutTestSystem

class PythonInOutTestSystem(pysim.cythonsystem.Sys):
    """Python representation of the cpp InOutTestSystem

    Used for testing that the cpp system behaves as the python system
    with regards to the input output handling
    """
    def __init__(self):
        self.add_input("input_scalar")
        self.add_input("input_vector",3)

        self.add_state("state_scalar","der_scalar")
        self.add_state("state_vector","der_vector", 3)

        self.add_output("input_output_scalar")
        self.add_output("input_output_vector",3)
        self.add_output("state_output_scalar")
        self.add_output("state_output_vector",3)

        self.inputs.input_scalar = 0.0
        self.inputs.input_vector = [0.0, 0.0, 0.0]

        self.outputs.input_output_scalar = 0.0
        self.outputs.input_output_vector = [0.0, 0.0, 0.0]
        self.outputs.state_output_scalar = 0.0
        self.outputs.state_output_vector = [0.0, 0.0, 0.0]

        self.states.state_scalar = 1.23
        self.states.state_vector = np.ones(3)*4.56
        self.ders.der_scalar = 0
        self.ders.der_vector = np.zeros(3)

    def do_step(self,dummy):
        """During a timestep we set the outputs to their respective inputs"""
        self.outputs.input_output_scalar = self.inputs.input_scalar
        self.outputs.input_output_vector = self.inputs.input_vector
        self.outputs.state_output_scalar = self.states.state_scalar
        self.outputs.state_output_vector = self.states.state_vector

class PythonAdder3D(pysim.cythonsystem.Sys):
    """Class used in testing, equivalent to the c++ Adder3D"""

    def __init__(self):
        self.add_input("input1",3)
        self.add_input("input2",3)
        self.inputs.input1 = [0.0, 0.0, 0.0]
        self.inputs.input2 = [0.0, 0.0, 0.0]
        self.add_output("output1",3)
        self.outputs.output1 = [0.0 ,0.0 ,0.0]

    def do_step(self,dummy):
        """Perform a timestep, adding the both inputs to create the 
        output.
        """
        i1 = np.array(self.inputs.input1)
        i2 = np.array(self.inputs.input2)
        self.outputs.output1 = i1+i2

class PythonAdder(pysim.cythonsystem.Sys):
    """Class used in testing, equivalent to the c++ Adder"""

    def __init__(self):
        self.add_input("input1")
        self.add_input("input2")
        self.inputs.input1 = 0.0
        self.inputs.input2 = 0.0
        self.add_output("output1")
        self.outputs.output1 = 0.0

    def do_step(self,dummy):
        """Perform a timestep, adding the both inputs to create the 
        output.
        """
        self.outputs.output1 = self.inputs.input1 + self.inputs.input2

__copyright__ = 'Copyright (c) 2014-2016 SSPA Sweden AB'

@pytest.mark.parametrize("adder_class",[Adder3D,PythonAdder3D])
def test_invalid_inputname(adder_class):
    """Test that an AttributeError is thrown if asking for a parameter that
    does not exist
    """
    sys = adder_class()
    with pytest.raises(AttributeError):
        dummy = sys.inputs.xyxyxy

@pytest.mark.parametrize("adder_class",[Adder3D,PythonAdder3D])
def test_invalid_outputname(adder_class):
    """Test that an AttributeError is thrown if asking for a variable that
    does not exist
    """
    sys = adder_class()
    with pytest.raises(AttributeError):
        dummy = sys.inputs.xyxyxy

@pytest.mark.parametrize("adder_class",[Adder3D,PythonAdder3D])
def test_invalid_input_dimension(adder_class):
    """Test that an ValueError is thrown if the number of elements in the
    parameter vector does not correspond with the number of values in the
    vector that it is being set to.
    """
    sys = adder_class()
    array2d = np.array((0.0, 0.0))
    with pytest.raises(ValueError):
        sys.inputs.input1 = array2d

@pytest.mark.parametrize("adder_class",[Adder3D,PythonAdder3D])
def test_invalid_vectorinput_type(adder_class):
    """Test that an TypeError is thrown when trying to set a vector parameter
    to a scalar.
    """
    sys = adder_class()
    with pytest.raises(TypeError):
        sys.inputs.input1 = 1

@pytest.mark.parametrize("adder_class",[Adder,PythonAdder])
def test_invalid_input_type(adder_class):
    """Test that an TypeError is thrown when trying to set a scalar parameter
    to a vector value.
    """
    sys = adder_class()
    array2d = np.array((0.0, 0.0))
    with pytest.raises(TypeError):
        sys.inputs.input1 = array2d


@pytest.mark.parametrize("adder_class",[Adder3D,PythonAdder3D])
def test_par_init(adder_class):
    """Tests that the par arrays are accessible and equal to 0"""
    sys = adder_class()
    x = sys.inputs.input1
    refarray = np.array((0.0, 0.0, 0.0))
    assert np.array_equal(x, refarray)

@pytest.mark.parametrize("adder_class",[Adder3D,PythonAdder3D])
def test_input_array_change(adder_class):
    """Tests that it is possible to change input array"""
    sys = adder_class()
    sys.inputs.input1 = (1.0, 2.0, 3.0)
    refarray = np.array((1.0, 2.0, 3.0))
    x = sys.inputs.input1
    assert np.array_equal(x, refarray)

@pytest.mark.parametrize("adder_class",[Adder,PythonAdder])
def test_input_scalar_change(adder_class):
    """Tests that it is possible to change input scalar"""
    sys = adder_class()
    testvalue = 1.234
    sys.inputs.input1 = testvalue
    x = sys.inputs.input1
    assert np.array_equal(x, testvalue)

def test_input_string_change():
    """Tests that it is possible to change a text input"""
    sys = ReadTextInput()
    testvalue = "hej.txt"
    sys.pars.filename = testvalue
    x = sys.pars.filename
    assert x == testvalue

def test_getinputdoc():
    """Tests that the documentation of an input is returned."""
    sys = VanDerPol()
    s = sys.inputs.__repr__()

    comparestr = "{:>10}  {:>8.3}  {}".format("b", "1.0", "Scaling coefficient")
    found = re.search(comparestr,s,re.MULTILINE)
    assert found

@pytest.mark.parametrize("adder_class",[Adder3D,PythonAdder3D])
def test_output_vector_init(adder_class):
    """Tests that the output arrays are accessible and equal to 0"""
    sys = adder_class()
    x = sys.outputs.output1
    refarray = np.array((0.0, 0.0, 0.0))
    assert np.array_equal(x, refarray)

@pytest.mark.parametrize("adder_class",[Adder,PythonAdder])
def test_output_scalar_init(adder_class):
    """Tests that the output scalars are accessible and equal to 0"""
    sys = adder_class()
    x = sys.outputs.output1
    assert np.array_equal(x, 0)

@pytest.mark.parametrize("adder_class",[Adder3D,PythonAdder3D])
def test_output_change(adder_class):
    """Tests that it is possible to change input array.
    To make sure that the input is actually used in the simulation
    this is done by setting a input, run a simulation and
    see that the output value has changed.
    """
    sys = adder_class()
    refarray1 = np.array((0.0, 0.0, 0.0))
    inputarray = (1.0, 2.0, 3.0)
    sys.inputs.input1 = inputarray
    x1 = sys.outputs.output1
    assert np.array_equal(x1, refarray1)
    sim = Sim()
    sim.add_system(sys)
    sim.simulate(1, 0.1)
    x2 = sys.outputs.output1
    assert np.array_equal(x2, inputarray)

@pytest.mark.parametrize("adder_class1,adder_class2",
                         [(Adder3D,Adder3D),
                          (PythonAdder3D,PythonAdder3D),
                          (Adder3D,PythonAdder3D),
                          (PythonAdder3D,Adder3D),
                         ])
def test_connected_system(adder_class1,adder_class2):
    """Check that it is possible to connect systems to each other 
    with boost vector outputs/inputs"""
    sys1 = adder_class1()
    sys2 = adder_class2()
    sys1.inputs.input1 = [1,2,3]
    sys1.connections.add_connection("output1",sys2,"input1")
    sim = Sim()
    sim.add_system(sys1)
    sim.add_system(sys2)
    assert np.all(sys2.outputs.output1 == [0.0, 0.0, 0.0])
    sim.simulate(1,0.1)
    assert np.all(sys2.outputs.output1 == [1.0, 2.0, 3.0])

@pytest.mark.parametrize("sys1_class,sys2_class",
                         [(InOutTestSystem,InOutTestSystem),
                          (PythonInOutTestSystem,PythonInOutTestSystem),
                          (InOutTestSystem,PythonInOutTestSystem),
                          (PythonInOutTestSystem,InOutTestSystem),
                         ])
def test_vector_scalar_conn(sys1_class,sys2_class):
    """Test that it is possible to connect vector to scalar

    An element of a vector output shall be possible to connect to an input
    scalar
    """
    sys1 = sys1_class()
    sys2 = sys2_class()
    sys3 = sys2_class()
    sys1.inputs.input_vector = [1,2,3]
    sys1.states.state_vector = [4,5,6]
    sys1.connections.add_connection("input_output_vector",sys2,"input_scalar",1)
    sys1.connections.add_connection("state_vector",sys3,"input_scalar",1)
    sim = Sim()
    sim.add_system(sys1)
    sim.add_system(sys2)
    sim.add_system(sys3)
    sim.simulate(0.1,0.1)
    assert sys2.outputs.input_output_scalar == 2.0
    assert sys3.outputs.input_output_scalar == 5.0

def test_der_as_output():
    """Test that it is possible to connect a derivative as output
    
    The der output should behave as a normal output. That this is the case is
    tested by connecting two systems to each output (der/output) and compare
    them.
    
    """
    sys1 = MassSpringDamper()
    sys2 = InOutTestSystem()
    sys3 = InOutTestSystem()
    sys1.connections.add_connection("dx2",sys2,"input_scalar")
    sys1.connections.add_connection("acceleration",sys3,"input_scalar")

    sys2.store("input_output_scalar")
    sys3.store("input_output_scalar")

    sim = Sim()
    sim.add_system(sys1)
    sim.add_system(sys2)
    sim.add_system(sys3)

    sim.simulate(1,0.1)

    output_from_der = sys2.res.input_output_scalar
    output_from_output = sys3.res.input_output_scalar
    assert np.allclose(output_from_der, output_from_output)

if __name__ == "__main__":
    test_vector_scalar_conn(PythonInOutTestSystem,InOutTestSystem)
