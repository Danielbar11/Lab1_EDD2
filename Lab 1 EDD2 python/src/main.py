from data_loader import DataLoader
import os

def main():
    csv_path = os.path.join("..", "dataset", "dataset_climate_change.csv")

    if not os.path.exists(csv_path):
        print("No se encontró el archivo")
        return  

    loader = DataLoader(csv_path)
    df = loader.load_data()

    print(df.head())

if __name__ == "__main__":
    main()
