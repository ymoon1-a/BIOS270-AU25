import argparse
import sqlite3
import numpy as np
import h5py
import pandas as pd

# -------------------------
# Database helper class
# -------------------------
class BacteriaDatabase:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def get_protein_ids_from_record_id(self, record_id):
        query = f"SELECT protein_id FROM gff WHERE record_id = '{record_id}'"
        df = pd.read_sql(query, self.conn)
        return df["protein_id"].dropna().tolist()
    
    def close(self):
        self.conn.close()


# -------------------------
# Main extraction logic
# -------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database_path", type=str, required=True)
    parser.add_argument("--h5_path", type=str, required=True)
    parser.add_argument("--record_id", type=str, required=True)
    parser.add_argument("--metric", type=str, required=True, choices=["mean", "mean_mid"])
    parser.add_argument("--output", type=str, default="output_embeddings.npy")
    args = parser.parse_args()

    # Load sqlite database
    db = BacteriaDatabase(args.database_path)
    protein_ids = db.get_protein_ids_from_record_id(args.record_id)
    print(f"Found {len(protein_ids)} proteins for record_id {args.record_id}")

    # Load HDF5 embeddings
    with h5py.File(args.h5_path, "r") as h5_file:
        # Select dataset name
        dataset_name = "mean_embeddings" if args.metric == "mean" else "mean_mid_embeddings"
        embeddings_ds = h5_file[dataset_name]

        # Build ID → index dictionary to avoid repeated .index() calls
        all_ids = list(h5_file["protein_ids"])
        id_to_index = {pid.decode("utf-8"): i for i, pid in enumerate(all_ids)}

        # Collect embeddings
        idx_list = []
        for pid in protein_ids:
            if pid in id_to_index:
                idx_list.append(id_to_index[pid])

        # Convert to numpy array
        embeddings = embeddings_ds[idx_list, :]  # shape = (N, 164)

    # Save output
    np.save(args.output, embeddings)
    print(f"Saved embeddings matrix of shape {embeddings.shape} to {args.output}")

    db.close()


if __name__ == "__main__":
    main()
