import os
from PIL import Image
from pillow_heif import register_heif_opener
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeicConverter:
    def __init__(self, output_format='jpg', quality=95, delete_originals=True):
        """
        Inicializa el convertidor HEIC.
        
        Args:
            output_format (str): Formato de salida ('jpg' o 'png')
            quality (int): Calidad para JPG (50-100)
            delete_originals (bool): Si eliminar archivos originales
        """
        # Registrar el opener para HEIF
        register_heif_opener()
        
        self.output_format = output_format.lower()
        self.quality = quality if output_format.lower() == 'jpg' else None
        self.delete_originals = delete_originals
        
        # Validar formato
        if self.output_format not in ['jpg', 'png']:
            raise ValueError("Formato debe ser 'jpg' o 'png'")
    
    def convert_file(self, heic_path):
        """
        Convierte un archivo HEIC individual.
        
        Args:
            heic_path (str): Ruta al archivo HEIC
            
        Returns:
            tuple: (success: bool, output_path: str, error: str)
        """
        try:
            # Generar ruta de salida
            base_name = os.path.splitext(heic_path)[0]
            output_path = f"{base_name}.{self.output_format}"
            
            # Evitar sobrescribir archivos existentes
            if os.path.exists(output_path):
                logger.info(f"Ya existe {output_path}, omitiendo...")
                return True, output_path, None
            
            # Abrir y convertir imagen
            with Image.open(heic_path) as imagen:
                # Configurar parámetros de guardado
                save_kwargs = {}
                if self.output_format == 'jpg':
                    save_kwargs['quality'] = self.quality
                    save_kwargs['optimize'] = True
                    # Convertir a RGB si tiene transparencia
                    if imagen.mode in ('RGBA', 'LA', 'P'):
                        imagen = imagen.convert('RGB')
                elif self.output_format == 'png':
                    save_kwargs['optimize'] = True
                
                # Guardar imagen convertida
                imagen.save(output_path, self.output_format.upper(), **save_kwargs)
            
            # Eliminar archivo original si se solicita
            if self.delete_originals:
                os.remove(heic_path)
                logger.info(f"Eliminado archivo original: {heic_path}")
            
            logger.info(f"Convertido: {heic_path} → {output_path}")
            return True, output_path, None
            
        except Exception as e:
            error_msg = f"Error al convertir {heic_path}: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def convert_folder(self, folder_path):
        """
        Convierte todos los archivos HEIC en una carpeta y subcarpetas.
        
        Args:
            folder_path (str): Ruta a la carpeta
            
        Returns:
            dict: Estadísticas de conversión
        """
        stats = {
            'converted': 0,
            'errors': 0,
            'skipped': 0,
            'error_files': []
        }
        
        # Buscar archivos HEIC recursivamente
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.heic'):
                    file_path = os.path.join(root, file)
                    
                    success, output_path, error = self.convert_file(file_path)
                    
                    if success:
                        if output_path and not os.path.exists(output_path.replace(f'.{self.output_format}', '.heic')):
                            stats['converted'] += 1
                        else:
                            stats['skipped'] += 1
                    else:
                        stats['errors'] += 1
                        stats['error_files'].append({
                            'file': file_path,
                            'error': error
                        })
        
        return stats
    
    def get_supported_formats(self):
        """
        Retorna los formatos soportados.
        
        Returns:
            dict: Formatos de entrada y salida soportados
        """
        return {
            'input': ['.heic', '.HEIC'],
            'output': ['.jpg', '.png']
        }