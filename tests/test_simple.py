"""
Test simple pour vérifier que pytest fonctionne
"""

def test_basic():
    """Test basique"""
    assert 1 + 1 == 2

def test_import():
    """Test des imports"""
    import sys
    import os
    assert sys.version_info >= (3, 7)
    assert os.path.exists("backend")

class TestSimple:
    """Classe de test simple"""
    
    def test_string(self):
        """Test de string"""
        assert "substans".upper() == "SUBSTANS"
    
    def test_list(self):
        """Test de liste"""
        my_list = [1, 2, 3]
        assert len(my_list) == 3
        assert sum(my_list) == 6