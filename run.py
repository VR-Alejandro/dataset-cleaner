import subprocess
import sys
import os
import time
import webbrowser

def main():
    print("Iniciando Dataset Cleaner...")

    # Ruta absoluta de la raíz del proyecto
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Ruta absoluta del directorio 'app'
    APP_DIR = os.path.join(ROOT_DIR, "app") if os.path.exists(os.path.join(ROOT_DIR, "app")) else ROOT_DIR
    
    # Rutas absolutas para el entorno virtual y el requirements.txt
    venv_dir = os.path.join(APP_DIR, ".venv")
    requirements_path = os.path.join(ROOT_DIR, "requirements.txt")

    # --- Gestión del entorno virtual (.venv) ---
    if not os.path.exists(venv_dir):
        print("No se detectó un entorno virtual. Creando (.venv) de forma aislada...")
        try:
            import venv
            venv.create(venv_dir, with_pip=True)
            print("Entorno virtual creado correctamente.")
        except Exception as e:
            print(f"Error al crear el entorno virtual: {e}")
            sys.exit(1)

    # Identificar el ejecutable de Python dentro del venv
    if sys.platform == "win32":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")


    # 1. Instalar dependencias utilizando la ruta del requirements.txt
    print("📥 Verificando e instalando dependencias en el entorno (.venv)...")
    try:
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", requirements_path])
    except Exception as e:
        print(f"Error al instalar dependencias: {e}")
        sys.exit(1)

    print("Dependencias listas y aisladas de tu sistema.")

    # 2. Configurar la URL de la app
    url = "http://localhost:5500"
    print(f"Abriendo la aplicación en tu navegador: {url}")
    
    time.sleep(1)
    webbrowser.open(url)

    # 3. Configuración de PYTHONPATH para imports relativos
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT_DIR + os.pathsep + env.get("PYTHONPATH", "")

    # 4. Lanzar el servidor Uvicorn (cwd en APP_DIR)
    print("Servidor en marcha. Presiona Ctrl+C para salir.\n")
    try:
        subprocess.run(
            [venv_python, "-m", "uvicorn", "main:app", "--port", "5500", "--host", "127.0.0.1"],
            cwd=APP_DIR,
            env=env
        )
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida. ¡Hasta la próxima!")

if __name__ == "__main__":
    main()