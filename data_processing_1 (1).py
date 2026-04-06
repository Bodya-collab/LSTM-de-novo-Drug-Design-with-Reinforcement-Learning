
def is_valid_smiles(smiles_str):
    """Проверяет, является ли SMILES химически валидным."""
    try:
        mol = Chem.MolFromSmiles(smiles_str)
        return mol is not None
    except:
        return False

def get_fingerprint(smiles_str, radius=2, n_bits=2048):
    """Превращает SMILES в числовой вектор современным методом MorganGenerator."""
    mol = Chem.MolFromSmiles(smiles_str)

    if mol is None:
        return None

    # Используем новый синтаксис, который требует RDKit
    mfpgen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    fp = mfpgen.GetFingerprint(mol)

    return np.array(fp)