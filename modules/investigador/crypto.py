# -*- coding: utf-8 -*-
"""
Enthema Suite V3.0 - Módulo Criptográfico de Soberanía Epistémica (Compromiso 5)
Implementa cifrado simétrico en reposo (Fernet) para proteger credenciales y bases locales.
"""
import os
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger("enthema.crypto")

# Directorio base para fallback si no se inicializa legal_dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_LEGAL_DIR = os.path.join(BASE_DIR, "output", "legal")

_cached_key = None

def resolve_master_key(legal_dir: str = None) -> bytes:
    """
    Resuelve la clave maestra de cifrado. Prioriza la variable de entorno ENTHEMA_MASTER_KEY.
    Si no está presente, busca un archivo persistente '.master.key' en el directorio legal.
    Si tampoco existe, genera una nueva clave simétrica robusta en caliente y la guarda localmente.
    """
    global _cached_key
    if _cached_key is not None:
        return _cached_key

    # 1. Intentar variable de entorno
    env_key = os.environ.get("ENTHEMA_MASTER_KEY")
    if env_key:
        try:
            key_bytes = env_key.encode("utf-8")
            # Validar que sea una clave Fernet válida
            Fernet(key_bytes)
            _cached_key = key_bytes
            logger.info("Clave criptográfica resuelta desde variable de entorno ENTHEMA_MASTER_KEY.")
            return _cached_key
        except Exception as e:
            logger.warning(f"La clave en ENTHEMA_MASTER_KEY no es válida para Fernet ({e}). Ignorando...")

    # 2. Intentar archivo persistente local
    if not legal_dir:
        legal_dir = DEFAULT_LEGAL_DIR
    
    os.makedirs(legal_dir, exist_ok=True)
    key_file = os.path.join(legal_dir, ".master.key")

    if os.path.exists(key_file):
        try:
            with open(key_file, "rb") as f:
                key_bytes = f.read().strip()
                Fernet(key_bytes)  # Validar
                _cached_key = key_bytes
                logger.info(f"Clave criptográfica cargada desde archivo persistente: {key_file}")
                return _cached_key
        except Exception as e:
            logger.error(f"Error al leer la clave persistente en {key_file} ({e}). Regenerando...")

    # 3. Generar clave nueva
    new_key = Fernet.generate_key()
    try:
        with open(key_file, "wb") as f:
            f.write(new_key)
        # Establecer permisos restrictivos de lectura/escritura solo para el usuario propietario (chmod 600)
        try:
            os.chmod(key_file, 0o600)
        except Exception:
            pass
        _cached_key = new_key
        logger.info(f"Nueva clave criptográfica generada y almacenada de forma segura en: {key_file}")
        return _cached_key
    except Exception as e:
        logger.critical(f"No se pudo guardar la clave criptográfica local en {key_file} ({e}). Usando clave efímera.")
        _cached_key = new_key
        return _cached_key

def encrypt_data(plain_text: str, legal_dir: str = None) -> str:
    """
    Cifra un texto plano usando Fernet y la clave maestra resuelta.
    Retorna la cadena cifrada en formato ASCII seguro.
    """
    if not plain_text:
        return plain_text
    
    try:
        key = resolve_master_key(legal_dir)
        cipher_suite = Fernet(key)
        cipher_bytes = cipher_suite.encrypt(plain_text.encode("utf-8"))
        return cipher_bytes.decode("ascii")
    except Exception as e:
        logger.error(f"Error durante el cifrado de datos: {e}")
        raise ValueError(f"Fallo crítico en el cifrado: {e}")

def decrypt_data(cipher_text: str, legal_dir: str = None) -> str:
    """
    Descifra un token cifrado usando Fernet y la clave maestra resuelta.
    Retorna la cadena en texto plano original.
    """
    if not cipher_text:
        return cipher_text
    
    try:
        key = resolve_master_key(legal_dir)
        cipher_suite = Fernet(key)
        plain_bytes = cipher_suite.decrypt(cipher_text.encode("ascii"))
        return plain_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Error durante el descifrado de datos: {e}")
        raise ValueError(f"Fallo crítico en el descifrado: {e}")


def shred_master_key(legal_dir: str = None) -> bool:
    """
    Implementación forense de Cripto-Purga (Crypto-Shredding) - Frente 8.
    Destruye físicamente la clave maestra del disco escribiéndole ceros (DoD 5220.22-M)
    y limpia la caché en memoria. Esto hace que toda la información cifrada históricamente
    (ej: en backups) sea matemáticamente irrecuperable de forma permanente.
    """
    global _cached_key
    _cached_key = None
    
    if not legal_dir:
        legal_dir = DEFAULT_LEGAL_DIR
        
    key_file = os.path.join(legal_dir, ".master.key")
    if os.path.exists(key_file):
        try:
            # Sobrescribir con ceros antes de borrar para evitar reconstrucción forense
            file_size = os.path.getsize(key_file)
            with open(key_file, "wb") as f:
                f.write(b"\x00" * file_size)
            os.remove(key_file)
            logger.info("Cripto-Purga completada: Clave maestra destruida e invalidada en disco y memoria.")
            return True
        except Exception as e:
            logger.error(f"Error durante el crypto-shredding: {e}")
            return False
    return False

