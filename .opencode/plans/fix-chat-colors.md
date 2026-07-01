# Plan: Arreglar Chat + Rediseñar Colores UNIMARC

## Archivos a modificar

### 1. `pages/03_Chat_IA.py` — Bug del Chat
**Problema:** Usa `st.empty()` + HTML custom con `st.markdown()`. Cuando Streamlit re-ejecuta el script durante el streaming, el placeholder se vuelve obsoleto y lanza excepción → `st.error()` rojo.

**Solución:** Reemplazar con `st.chat_message()` nativo de Streamlit, que maneja correctamente el estado entre reruns.

```python
# Antes (roto):
response_container = st.empty()
response_container.markdown(...)
for chunk in consultar(prompt):
    full_response += chunk
    response_container.markdown(...)

# Después (arreglado):
with st.chat_message("assistant"):
    placeholder = st.empty()
    for chunk in consultar(prompt):
        full_response += chunk
        placeholder.markdown(full_response + "▌")
    placeholder.markdown(full_response)
```

### 2. `static/styles.css` — Rediseño completo de colores
- **Sidebar:** Fondo `#C41230` (rojo oscuro), texto blanco
- **Fondo general:** `#FAFAFA`
- **Hero:** Gradiente rojo más intenso
- **Tarjetas:** Bordes rojos, sombras rojas al hover
- **Botones primarios:** Rojo UNIMARC
- **Inputs:** Borde rojo al focus
- **Chat:** Burbuja usuario roja, burbuja bot blanca con borde rojo
- **Mascota Uni:** Ajustada para fondo de sidebar rojo

### 3. `main.py` — Sidebar roja con logo
- Insertar logo `OIP.webp` en sidebar y login
- Cambiar "Salir" a botón blanco con borde
- Adaptar la mascota Uni (burbuja de diálogo con fondo blanco)
- Timer de sesión en texto blanco

### 4. Mover logo
- `OIP.webp` → `static/logo.webp`

### 5. `templates/index.html` (Flask)
- Si es necesario, actualizar referencia al logo

## Flujo de implementación
1. Mover OIP.webp a static/
2. Reescribir pages/03_Chat_IA.py
3. Reescribir static/styles.css
4. Actualizar main.py (sidebar + login)
5. Verificar con `streamlit run main.py`
