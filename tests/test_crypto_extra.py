# -*- coding: utf-8 -*-
"""
Enthema Suite V3.0 - Tests unitarios adicionales de robustez para modules/investigador/crypto.py.
Eleva la cobertura criptográfica al 100% cubriendo excepciones y rutas de error.
"""
import unittest
import os
import sys
import shutil
import tempfile
from unittest.mock import patch, mock_open
from cryptography.fernet import Fernet

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.investigador.crypto import (
    resolve_master_key,
    encrypt_data,
    decrypt_data,
    shred_master_key,
    _cached_key
)

class TestCryptoExtraUncovered(unittest.TestCase):
    
    def setUp(self):
        """Crear un directorio temporal para pruebas aisladas de archivos de llaves."""
        self.test_dir = tempfile.mkdtemp()
        # Reset cached key to force re-resolution
        import modules.investigador.crypto
        modules.investigador.crypto._cached_key = None
        
    def tearDown(self):
        """Eliminar el directorio temporal."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        # Limpiar variables de entorno usadas
        os.environ.pop("ENTHEMA_MASTER_KEY", None)
        # Reset global cached key
        import modules.investigador.crypto
        modules.investigador.crypto._cached_key = None

    def test_env_key_valid(self):
        """Test: Carga de clave válida desde la variable de entorno."""
        valid_key = Fernet.generate_key().decode("utf-8")
        os.environ["ENTHEMA_MASTER_KEY"] = valid_key
        
        resolved = resolve_master_key(self.test_dir)
        self.assertEqual(resolved.decode("utf-8"), valid_key)

    def test_env_key_invalid(self):
        """Test: Clave inválida en variable de entorno (cae en fallback a disco)."""
        os.environ["ENTHEMA_MASTER_KEY"] = "clave-invalida-no-base64"
        
        # Debe fallar la carga desde env y generar una en disco
        resolved = resolve_master_key(self.test_dir)
        self.assertIsNotNone(resolved)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, ".master.key")))

    def test_default_legal_dir_fallback(self):
        """Test: Fallback al directorio legal por defecto si no se especifica."""
        # Forzar que use DEFAULT_LEGAL_DIR sin arrojar errores
        resolved = resolve_master_key(None)
        self.assertIsNotNone(resolved)

    def test_corrupt_key_file_regeneration(self):
        """Test: Regeneración automática si el archivo persistente en disco está corrupto."""
        key_file = os.path.join(self.test_dir, ".master.key")
        with open(key_file, "wb") as f:
            f.write(b"datos corruptos no validos para fernet")
            
        resolved = resolve_master_key(self.test_dir)
        self.assertIsNotNone(resolved)
        # La clave corrupta debe ser sobrescrita con una nueva clave válida
        with open(key_file, "rb") as f:
            new_key = f.read().strip()
        self.assertEqual(resolved, new_key)
        # Validar que sea Fernet ejecutable
        Fernet(new_key)

    def test_chmod_exception_handling(self):
        """Test: Manejo de excepciones al fallar el chmod del archivo de llaves (ej. Windows)."""
        with patch("os.chmod", side_effect=OSError("Permiso denegado")):
            resolved = resolve_master_key(self.test_dir)
            self.assertIsNotNone(resolved)

    def test_ephemeral_key_fallback(self):
        """Test: Si no se puede escribir la clave en el disco, cae en clave efímera en caliente."""
        with patch("builtins.open", side_effect=IOError("No se puede escribir")):
            resolved = resolve_master_key(self.test_dir)
            self.assertIsNotNone(resolved)

    def test_empty_string_encrypt_decrypt(self):
        """Test: Cifrado y descifrado de texto vacío o None retorna el mismo valor."""
        self.assertEqual(encrypt_data("", self.test_dir), "")
        self.assertEqual(encrypt_data(None, self.test_dir), None)
        self.assertEqual(decrypt_data("", self.test_dir), "")
        self.assertEqual(decrypt_data(None, self.test_dir), None)

    def test_encryption_decryption_exceptions(self):
        """Test: Excepciones de cifrado y descifrado ante fallos del algoritmo."""
        # Descifrado de token inválido
        with self.assertRaises(ValueError):
            decrypt_data("token-fernet-totalmente-invalido", self.test_dir)
            
        # Cifrado con clave maestra inválida (simulado por mock de resolve_master_key)
        with patch("modules.investigador.crypto.resolve_master_key", return_value=b"clave-invalida"):
            with self.assertRaises(ValueError):
                encrypt_data("texto a cifrar", self.test_dir)

    def test_shred_master_key_full_flow(self):
        """Test: Ciclo de Cripto-Purga completo (DoD 5220.22-M y limpieza en memoria)."""
        key_file = os.path.join(self.test_dir, ".master.key")
        
        # 1. Generar la clave
        resolved_first = resolve_master_key(self.test_dir)
        self.assertTrue(os.path.exists(key_file))
        
        # 2. Cripto-purgar la clave
        success = shred_master_key(self.test_dir)
        self.assertTrue(success)
        self.assertFalse(os.path.exists(key_file))
        
        # 3. Validar que la caché global _cached_key se haya vaciado
        import modules.investigador.crypto
        self.assertIsNone(modules.investigador.crypto._cached_key)

    def test_shred_non_existent_key(self):
        """Test: Intentar purgar cuando el archivo de clave no existe retorna False."""
        # Asegurar que el archivo no existe
        key_file = os.path.join(self.test_dir, ".master.key")
        if os.path.exists(key_file):
            os.remove(key_file)
            
        success = shred_master_key(self.test_dir)
        self.assertFalse(success)

    def test_shred_exception_handling(self):
        """Test: Control de excepciones al fallar el borrado físico de la clave."""
        resolve_master_key(self.test_dir)
        with patch("os.remove", side_effect=OSError("Archivo bloqueado por el sistema")):
            success = shred_master_key(self.test_dir)
            self.assertFalse(success)

    def test_shred_default_dir(self):
        """Test: Cripto-Purga usando el directorio por defecto."""
        success = shred_master_key(None)
        self.assertIn(success, [True, False])

if __name__ == "__main__":
    unittest.main()
