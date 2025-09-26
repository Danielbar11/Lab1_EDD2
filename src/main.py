from data_loader import DataLoader
from interface import Interface
import os

def main():
    csv_path = os.path.join(os.getcwd(), "dataset", "dataset_climate_change.csv")

    if not os.path.exists(csv_path):
        print("No se encontró el archivo")
        return  

    loader = DataLoader(csv_path)
    df = loader.load_data()

    app = Interface(df)
    app.mainloop()

if __name__ == "__main__":
    main()
