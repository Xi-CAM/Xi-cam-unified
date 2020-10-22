from typing import Tuple
import pytest
import numpy as np

from xicam.core import execution
from xicam.core.execution import localexecutor
from xicam.core.execution.workflow import Graph, Workflow
from xicam.core.intents import PlotIntent, ImageIntent
from xicam.plugins import OperationPlugin
from xicam.plugins.operationplugin import output_names, operation, display_name, intent
from pyqtgraph.parametertree import Parameter


@pytest.fixture()
def graph():
    return Graph()


@pytest.fixture()
def double_and_triple_op():
    @operation
    @output_names("double", "triple")
    def double_and_triple(n: int) -> Tuple[int, int]:
        return 2*n, 3*n
    return double_and_triple()


@pytest.fixture()
def square_op():
    @operation
    def square(n: int) -> int:
        return n * n

    return square()


@pytest.fixture()
def sum_op():
    @operation
    def sum(n1: int, n2: int) -> int:
        return n1 + n2

    return sum()


@pytest.fixture()
def negative_op():
    @operation
    def negative(num: int) -> int:
        return -1 * num

    return negative()


@pytest.fixture()
def a_op():
    @operation
    @output_names("n")
    def a(n: int) -> int:
        return n + 1
    return a()


@pytest.fixture()
def b_op():
    @operation
    @output_names("n")
    def b(n: int) -> int:
        return n - 1
    return b()


@pytest.fixture()
def c_op():
    @operation
    @output_names("n")
    def c(n: int) -> int:
        return n * n
    return c()


@pytest.fixture()
def plot_op():
    @operation
    @output_names('x', 'y')
    @intent(PlotIntent, name='Example Plot', output_map={'x':'x', 'y':'y'})
    def plot() -> Tuple[np.ndarray, np.ndarray]:
        return np.arange(100), np.random.random((100,))
    return plot()


@pytest.fixture()
def image_op():
    @operation
    @output_names('image')
    @intent(ImageIntent, name='Example Image', output_map={'image':'image'})
    def image() -> np.ndarray:
        return np.random.random((100,100))
    return image()


@pytest.fixture()
def simple_workflow(square_op, sum_op):
    from xicam.core.execution.workflow import Workflow

    wf = Workflow()

    square = square_op
    square2 = square_op.__class__()
    square2.filled_values["n"] = 2

    wf.add_operation(square)
    wf.add_operation(square2)
    wf.add_operation(sum_op)
    wf.add_link(square, sum_op, "square", "n1")
    wf.add_link(square2, sum_op, "square", "n2")

    return wf


@pytest.fixture()
def custom_parameter_op():
    class CustomParameterOp(OperationPlugin):
        def __init__(self):
            super(CustomParameterOp, self).__init__()
            self.value = False

        def _func(self):
            return self.value

        def as_parameter(self):
            return [{'name':'test', 'type':'bool'}]

        def wireup_parameter(self, parameter:Parameter):

            parameter.child('test').sigValueChanged.connect(lambda value: print(value))

    return CustomParameterOp


@pytest.fixture()
def custom_parameter_workflow(custom_parameter_op):
    from xicam.core.execution.workflow import Workflow

    wf = Workflow()

    custom_parameter_op = custom_parameter_op()

    wf.add_operation(custom_parameter_op)
    return wf


@pytest.fixture()
def intents_workflow(plot_op, image_op):
    from xicam.core.execution.workflow import Workflow

    wf = Workflow()

    wf.add_operation(plot_op)
    wf.add_operation(image_op)

    return wf
