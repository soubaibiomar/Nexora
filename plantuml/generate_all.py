"""
Génère les images PNG pour tous les fichiers .puml du dossier plantuml/
en utilisant le serveur PlantUML public.
"""
import os
import glob
import plantuml

def main():
    puml_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(puml_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    server = plantuml.PlantUML(url="http://www.plantuml.com/plantuml/png/")

    puml_files = sorted(glob.glob(os.path.join(puml_dir, "*.puml")))

    if not puml_files:
        print("Aucun fichier .puml trouvé.")
        return

    print(f"Trouvé {len(puml_files)} fichiers .puml\n")

    for puml_file in puml_files:
        basename = os.path.splitext(os.path.basename(puml_file))[0]
        output_file = os.path.join(output_dir, f"{basename}.png")

        print(f"  Génération : {basename}.puml -> {basename}.png ... ", end="", flush=True)
        try:
            # Read the puml content
            with open(puml_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Use the server to generate
            result = server.processes(content)
            
            # Write the PNG
            with open(output_file, "wb") as f:
                f.write(result)
            
            print(f"OK ({os.path.getsize(output_file):,} bytes)")
        except Exception as e:
            print(f"ERREUR: {e}")

    print(f"\nTerminé ! Images générées dans : {output_dir}")

if __name__ == "__main__":
    main()
