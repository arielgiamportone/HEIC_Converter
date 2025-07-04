import streamlit as st
import zipfile
import io
import os
from .converter import HeicConverter
from PIL import Image
import tempfile
import shutil

# Configuración de la página
st.set_page_config(
    page_title="HEIC to JPG/PNG Converter",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título y descripción
st.title("🖼️ HEIC to JPG/PNG Converter")
st.markdown("""
### Convierte tus archivos HEIC a JPG o PNG fácilmente
Sube una carpeta comprimida (.zip) con archivos HEIC y descarga los archivos convertidos.
""")

# Sidebar para configuraciones
with st.sidebar:
    st.header("⚙️ Configuraciones")
    
    # Formato de salida
    output_format = st.selectbox(
        "Formato de salida:",
        ["JPG", "PNG"],
        index=0
    )
    
    # Calidad para JPG
    if output_format == "JPG":
        quality = st.slider(
            "Calidad JPG:",
            min_value=50,
            max_value=100,
            value=95,
            step=5
        )
    else:
        quality = None
    
    # Opción para eliminar archivos originales
    delete_originals = st.checkbox(
        "Eliminar archivos HEIC originales",
        value=True
    )
    
    st.markdown("---")
    st.markdown("""
    **Formatos soportados:**
    - Entrada: .heic, .HEIC
    - Salida: .jpg, .png
    
    **Tamaño máximo:** 200MB
    """)

# Área principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📁 Subir Archivos")
    
    # Upload de archivo ZIP
    uploaded_file = st.file_uploader(
        "Selecciona un archivo ZIP con imágenes HEIC:",
        type=['zip'],
        help="Sube un archivo .zip que contenga archivos .heic"
    )
    
    if uploaded_file is not None:
        # Mostrar información del archivo
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        st.info(f"📊 Archivo: {uploaded_file.name} ({file_size:.2f} MB)")
        
        if file_size > 200:
            st.error("❌ El archivo es demasiado grande. Máximo 200MB.")
            st.stop()
        
        # Botón para procesar
        if st.button("🚀 Convertir Archivos", type="primary"):
            with st.spinner("Procesando archivos..."):
                try:
                    # Crear directorio temporal
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Extraer ZIP
                        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                        
                        # Inicializar convertidor
                        converter = HeicConverter(
                            output_format=output_format.lower(),
                            quality=quality,
                            delete_originals=delete_originals
                        )
                        
                        # Convertir archivos
                        result = converter.convert_folder(temp_dir)
                        
                        # Mostrar resultados
                        if result['converted'] > 0:
                            st.success(f"✅ {result['converted']} archivos convertidos exitosamente")
                            
                            if result['errors'] > 0:
                                st.warning(f"⚠️ {result['errors']} archivos con errores")
                            
                            # Crear ZIP con archivos convertidos
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                for root, dirs, files in os.walk(temp_dir):
                                    for file in files:
                                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                                            file_path = os.path.join(root, file)
                                            arcname = os.path.relpath(file_path, temp_dir)
                                            zip_file.write(file_path, arcname)
                            
                            zip_buffer.seek(0)
                            
                            # Botón de descarga
                            st.download_button(
                                label="📥 Descargar Archivos Convertidos",
                                data=zip_buffer.getvalue(),
                                file_name=f"converted_images_{output_format.lower()}.zip",
                                mime="application/zip"
                            )
                        else:
                            st.error("❌ No se encontraron archivos HEIC para convertir")
                            
                except Exception as e:
                    st.error(f"❌ Error durante la conversión: {str(e)}")

with col2:
    st.header("📋 Instrucciones")
    st.markdown("""
    1. **Prepara tus archivos:**
       - Coloca todos los archivos HEIC en una carpeta
       - Comprime la carpeta en un archivo .zip
    
    2. **Configura las opciones:**
       - Elige el formato de salida (JPG/PNG)
       - Ajusta la calidad si es necesario
    
    3. **Sube y convierte:**
       - Selecciona tu archivo .zip
       - Haz clic en "Convertir Archivos"
    
    4. **Descarga:**
       - Descarga el archivo .zip con las imágenes convertidas
    """)
    
    # Estadísticas de la sesión
    if 'total_converted' not in st.session_state:
        st.session_state.total_converted = 0
    
    st.markdown("---")
    st.metric(
        "Archivos convertidos en esta sesión",
        st.session_state.total_converted
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Desarrollado con ❤️ usando Streamlit | 
    <a href='https://github.com/tu-usuario/heic-converter-app' target='_blank'>Ver en GitHub</a></p>
</div>
""", unsafe_allow_html=True)