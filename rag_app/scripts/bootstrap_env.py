import os
import shutil
import sys
from pathlib import Path

# Códigos de color ANSI para una UX de terminal moderna
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def bootstrap():
    """
    Configura el entorno de desarrollo local.
    1. Crea .env desde la plantilla .env.example
    2. Solicita la GEMINI_API_KEY al usuario
    """
    print(f"{Colors.HEADER}{Colors.BOLD}🤖 Iniciando Bootstrap del Entorno de Desarrollo{Colors.ENDC}")
    
    # Resolver rutas absolutas basándose en la ubicación de este script
    # Script está en: rag_app/scripts/bootstrap_env.py
    # Raíz del proyecto (rag_app) es: parent.parent
    current_script = Path(__file__).resolve()
    rag_app_dir = current_script.parent.parent
    
    env_path = rag_app_dir / ".env"
    
    # Buscamos el ejemplo en varios lugares posibles por robustez
    possible_examples = [
        rag_app_dir / "config" / ".env.example", # Recomendado
        rag_app_dir / ".env.example"             # Alternativa raíz app
    ]
    
    example_path = next((p for p in possible_examples if p.exists()), None)

    # 1. Validación de Pre-requisitos
    if not example_path:
        print(f"{Colors.FAIL}❌ Error Crítico: No se encontró .env.example.{Colors.ENDC}")
        print(f"   Asegúrate de haber creado 'rag_app/.env.example' antes de correr esto.")
        sys.exit(1)

    # 2. Verificar si ya existe configuración
    if env_path.exists():
        print(f"{Colors.OKBLUE}ℹ️  El archivo .env ya existe.{Colors.ENDC}")
        print("   No se realizarán cambios para proteger tu configuración actual.")
        return

    # 3. Creación del archivo desde plantilla
    print(f"{Colors.WARNING}⚠️  Configuración local no detectada.{Colors.ENDC}")
    print(f"   Clonando plantilla desde: {example_path.name}...")
    
    try:
        shutil.copy(example_path, env_path)
        print(f"{Colors.OKGREEN}✅ Archivo base creado.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error al copiar archivo: {e}{Colors.ENDC}")
        sys.exit(1)

    # 4. Automatización BYOK (Input Interactivo)
    print("\n" + "-"*60)
    print(f"{Colors.BOLD}🔑 CONFIGURACIÓN DE CREDENCIALES (BYOK){Colors.ENDC}")
    print("   Para funcionar, el bot necesita una API Key de Google Gemini.")
    print("   Obtenla gratis aquí: https://aistudio.google.com/app/apikey")
    print("-" * 60)
    
    api_key = input(f"{Colors.OKBLUE}Pegá tu GEMINI_API_KEY aquí (Enter para omitir): {Colors.ENDC}").strip()

    if api_key:
        try:
            # Leemos el archivo recién creado
            with open(env_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Reemplazamos la variable vacía o agregamos al final
            if "GEMINI_API_KEY=" in content:
                new_content = content.replace("GEMINI_API_KEY=", f"GEMINI_API_KEY={api_key}")
            else:
                new_content = content + f"\nGEMINI_API_KEY={api_key}\n"
            
            # Guardamos
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            print(f"\n{Colors.OKGREEN}✨ ¡Configuración completada exitosamente!{Colors.ENDC}")
            print(f"   Archivo guardado en: {env_path}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error escribiendo la clave: {e}{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}⚠️  Has omitido la clave.{Colors.ENDC}")
        print(f"   Recuerda editar {env_path} manualmente antes de iniciar el servidor.")

if __name__ == "__main__":
    bootstrap()