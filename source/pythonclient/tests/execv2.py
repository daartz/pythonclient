import time
import pygetwindow


def main():
    # Votre code principal ici
    while True:
        # Vérifie si la fenêtre CMD est toujours ouverte
        cmd_window = pygetwindow.getWindowsWithTitle("MaFenetreCMD")
        if not cmd_window:
            print("La fenêtre CMD a été fermée. Arrêt du script.")
            break

        # Votre logique de traitement continue ici
        # Assurez-vous d'inclure des appels à time.sleep() ou des points de sortie de la boucle.

        # Exemple : Attendre 1 seconde avant de vérifier à nouveau
        time.sleep(1)


if __name__ == "__main__":
    main()
