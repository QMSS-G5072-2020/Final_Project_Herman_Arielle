from final_project_herman_arielle import __version__
from final_project_herman_arielle import final_project_herman_arielle
import pytest

def test_version():
    assert __version__ == '0.1.0'

with pytest.raises(AssertionError):
    collections(5)
    structures(5)
    difference_two("x", [1,2])
    difference_two([1,2], "x")
    
with pytest.raises(TypeError):
    difference_two("x")